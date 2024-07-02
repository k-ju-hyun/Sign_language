from django.shortcuts import render
from django.utils import timezone
import logging
from django.conf import settings
from django.core.files.storage import default_storage
import numpy as np
import cv2
import string
import mlflow
import mlflow.keras
from chatgpt.views import chatGPT
logger = logging.getLogger('mylogger')
#signlanguage/models.py의 Result 모델을 import한다.
from .models import ChatResult, Result

def getChatResult(self, id):
    query = "SELECT * FROM selfsignlanguagechat_ChatResult WHERE id = {0}".format(id)
    logger.info(">>>>>>>> getChatResult SQL : " + query)
    chatResult = self.t_exec(query)


def index(req):
    root_style_urls = ['css/common.css', 'css/header.css', 'css/footer.css', 'css/color2.css']
    style_urls = ['selflanguagechat/self_style.css']
    context = { 'root_style_urls': root_style_urls,
                'style_urls': style_urls }
    return render(req, 'selflanguagechat/index.html', context)

def chat(req):
    root_style_urls = ['css/common.css', 'css/header.css', 'css/footer.css', 'css/color2.css']
    style_urls = ['selflanguagechat/chat_style.css']
    
    if req.method == 'POST' and req.FILES['files']:
        results=[]
        #form에서 전송한 파일을 획득한다.
        #각 파일별 예측 결과들을 모아야 질문을 위한 언어가 완성된다.
        files = req.FILES.getlist('files')
        chatGptPrompt = ""
        for idx,file in enumerate(files, start=0):
            # files:

            # logger.error('file', file)
            # class names 준비
            class_names = list(string.ascii_lowercase)
            class_names = np.array(class_names)


            # mlflow 로딩
            mlflow_uri="http://mini7-mlflow.carpediem.so/"
            mlflow.set_tracking_uri(mlflow_uri)
            model_uri = "models:/Sign_Signal/production"
            model = mlflow.keras.load_model(model_uri)


            # history 저장을 위해 객체에 담아서 DB에 저장한다.
            # 이때 파일시스템에 저장도 된다.
            result = Result()
            result.image = file
            result.pub_date = timezone.datetime.now()
            result.save()


            # 흑백으로 읽기
            img = cv2.imread(result.image.path, cv2.IMREAD_GRAYSCALE)

            # 크기 조정
            img = cv2.resize(img, (28, 28))

            # input shape 맞추기
            test_sign = img.reshape(1, 28, 28, 1)

            # 스케일링
            test_sign = test_sign / 255.

            # 예측 : 결국 이 결과를 얻기 위해 모든 것을 했다.
            pred = model.predict(test_sign)
            pred_1 = pred.argmax(axis=1)

            result_str = class_names[pred_1][0]


            #결과를 DB에 저장한다.
            result.result = result_str
            # result.is_correct = 
            result.save()
            results.append(result)

            #result.result의 결과를 하나씩 chatGptPrompt에 추가한다.
            chatGptPrompt += result.result
        
        #질문을 DB에 저장한다.
        chatResult = ChatResult()
        chatResult.prompt = chatGptPrompt
        chatResult.pub_date = timezone.datetime.now()
        chatResult.save()


        #저장된 질문을 DB에서 가져온다.
        selectedChatResult = ChatResult.objects.get(id=chatResult.id)

        #chatGptPrompt를 chatGPT에게 전달한다.
        content = chatGPT(selectedChatResult.prompt)
        selectedChatResult.content = content
        selectedChatResult.save()
        
        

        context = {
        'question': selectedChatResult.prompt,
        'result': selectedChatResult.content,
        'root_style_urls': root_style_urls,
        'style_urls': style_urls
    }

    return render(req, 'selflanguagechat/result.html', context)

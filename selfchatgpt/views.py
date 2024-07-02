from django.shortcuts import render
import openai


#Chat gpt api에 질문에 대한 결과 요청
def chatGpt(prompt):
    #api 키
    openai.api_key = ""

    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]#질문 입력
    )
    result = completion.choices[0].message.content
    return result

#index.html(메인 페이지)
def index(req):
    root_style_urls = ['css/common.css', 'css/header.css', 'css/footer.css', 'css/color2.css']
    style_urls = ['selfgpt/index.css']
    context = { 'root_style_urls': root_style_urls,
                'style_urls': style_urls }
    return render (req, 'selfgpt/index.html', context)

#result.html(결과 페이지)
def chat(req):
    root_style_urls = ['css/common.css', 'css/header.css', 'css/footer.css', 'css/color2.css']
    style_urls = ['selfgpt/index.css']
    prompt = req.POST.get('question')
    result = chatGpt(prompt)
    
    context = {
        'question': prompt,#gpt에게 입력한 질문
        'result': result,#질문에 대한 gpt의 답변
        'root_style_urls': root_style_urls,
        'style_urls': style_urls
    }
    return render(req, 'selfgpt/result.html', context)
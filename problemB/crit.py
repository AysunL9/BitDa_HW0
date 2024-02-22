import openai
import re
client =openai.Client(api_key='')

def cirit(document):
    Γ=0
    Ω=generate_claim(document)
    R=find_supporting_reasons(Ω)
    R_prime=find_counter_reasons(Ω)
    validted_R,_=validate_reasons(R,Ω)
    for score_r,score_θ in validted_R:
        Γ+= score_r*score_θ
    validted_R_prime,_=validate_reasons(R_prime,Ω)
    for score_r,score_θ in validted_R_prime:
        Γ+= score_r*score_θ
    Γ=Γ/(len(R)+len(R_prime))
    conclusion=client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user",
                "content": f"Give the conclusion of {Ω}"
                }
            ],
            max_tokens=50
        )
    return Γ,conclusion.choices[0].message.content

def generate_claim(document):
    response=client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{
                "role": "user",
                "content": f"Idnetify a cliam in the following text:{document}"
                }],
        max_tokens=50,
        temperature=0.7
    )
    return response.choices[0].message.content.strip()

def find_supporting_reasons(claim):
    response=client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "user",
                "content": f"What are supporting reasons for the claim:{claim}"
                }
            ],
        max_tokens=150,
        temperature=0.7
    )
    reasons=response.choices[0].message.content.strip().split('\n')
    return [reason.strip() for reason in reasons if reason.strip()]

def find_counter_reasons(claim):
    response=client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "user",
                "content": f"What are strong counter reasons against the claim:{claim}"
                }
            ],
        max_tokens=150,
        temperature=0.7
    )
    counter_reasons=response.choices[0].message.content.strip().split('\n')
    return [reason.strip() for reason in counter_reasons if reason.strip()]

def validate_reasons(reasons,claim):
    validate_reasons=[]
    total_score=0
    for reason in reasons:
        response=client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user",
                "content": f"Rate argumant validity and source credibility between 1 to 10(strongest).How strongly does the '{reason}' support the claim:'{claim}'?(answer two scores only)"
                }
            ],
            max_tokens=50
        )
        try:
            score_text=response.choices[0].message.content.strip()
            ratings=re.findall(r'\d+', score_text)
            score_r=int(ratings[0])
            score_θ=int(ratings[1])
        except IndexError:
            score_r=5
            score_θ=5
        
        validate_reasons.append((score_r,score_θ))
        total_score+=score_θ
    
    average_score=total_score/len(reasons) if reasons else 0
    return validate_reasons,average_score


score,conclusion=cirit("Is killing vampires immoral?")
while True:
    score_n,conclusion_n=cirit("Is killing vampires immoral?")
    if score_n<score:
        break
    else:
        score=score_n
        conclusion=conclusion_n
print("Is killing vampires immoral?\n","Score:",score,"Conclusion:",conclusion)


score,conclusion=cirit("Is meat eating immoral?")
while True:
    score_n,conclusion_n=cirit("Is meat eating immoral?")
    if score_n<score:
        break
    else:
        score=score_n
        conclusion=conclusion_n
print("Is meat eating immoral?\n","Score:",score,"\nConclusion:",conclusion)

# 評估每輪辯論的驗證分數，如果分數下降，則停止辯論階段。然後，進行最後的總結。最後，使用第三個GPT模型來創建最終的判斷
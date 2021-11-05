# 2018 빅데이터 해커톤 추천 시스템 코드
import sys
import openpyxl
import pandas as pd
import itertools
import json

age, height, weight, job, edu, gender, child = [a for item in sys.argv[1:]]

# gender 남성 1 여성 2
# edu 1~4 중졸 - 대졸이상
# job 1~9 직종분류
# child 자녀있음 1 자녀없음 2

insurance_list = []


# 연령에 따른 발병 확률 높은 질병 보험 (플로우에 보윤 텍스트로 올린 내용)
# 보장 범위 겹친 보험은 제외하고 최소로
age = int(age)
if age <= 39:
    insurance_list.extend(['(무)하나로OK(건강)'])
elif 40 < age <= 45:
    insurance_list.extend(['(무)하나로OK(건강)', '(무)하나로OK(중대질병)'])
elif 45 < age <= 49:
    insurance_list.append('(무)건강클리닉')


# BMI에 따른 질병 추천 -> 23을 넘으면 3대성인병
# BMI 계산식: 몸무게/(신장 = m 기준)^2
BMI = int(weight) / ((int(height)/100)**2)
if BMI > 23:
    insurance_list.extend(['(무)실속정기1종순수'])


# 직종에 따른 질병 추천
"""
int(job)
관리자 1
전문가 및 관련 종사자 2
사무 종사자 3
서비스 종사자 4
판매 종사자 5
농림어업 숙련 종사자 6
기능원 및 관련 기능 종사자 7
장치, 기계조작 및 조립 종사자 8
단순노무 종사자 9
"""
# 전체 고용조사통계의 1~9와 직종과 질병 상관관계의 1~7 인덱스때문에 겹치는 애들 설정 
if int(job) == 2:
    minijob = 1
if int(job) == 3:
    minijob = 2
if int(job) == 4:
    minijob = 3
if int(job) == 6:
    minijob = 4
if int(job) == 7:
    minijob = 5
if int(job) == 8:
    minijob = 6
if int(job) == 9:
    minijob = 7


# 직종과 질병 상관관계 데이터 불러옴 (광진씨가 플로우에 올려주신 것을 엑셀로 정리함)
wb = openpyxl.load_workbook('D:\Hackerthon_result\job_disease.xlsx')
ws = wb.active

if int(job) in [2, 3, 4, 6, 7, 8, 9]:
    insurance_list.extend(list(list(ws.values)[1:][minijob-1]))

wb.close()

print("1")


# 패키지 필터 기준 - 직종에 따른 상한가 계산
wb = pd.read_excel('D:\Hackerthon_result\job_rage.xlsx')
df = pd.DataFrame(wb)

# 엑셀에 age가 문자열로 되어있어서 따로 인코딩해줌
if int(age) <= 34:
    age_group = 1
elif 35< int(age) <= 39:
    age_group = 2
elif 40 < int(age) <= 44:
    age_group = 3
elif 45 < int(age) <= 49:
    age_group= 4

# default_average 기준
month_range = 3253000

# 엑셀 파일에 있는대로 성별, 연령별, 직종별 예상 임금으로 그 사람의 임금 예측하기
if int(df[(df.iloc[:,0]==int(job))&(df.iloc[:,1]==int(edu))&(df.iloc[:,2]==gender)&(df.iloc[:,3]==age_group)].iloc[:,-1]):
    month_rage = int(df[(df.iloc[:,0]==int(job))&(df.iloc[:,1]==int(edu))&(df.iloc[:,2]==gender)&(df.iloc[:,3]==age_group)].iloc[:,-1])*1000
                     
# 상한 기준은 보험료 / 30~40대 평균적인 임금
up_limit = month_range * 0.0215

# 체크 - 보험 이름이 겹치는 것 빼기
insurance_list = set(insurance_list)

print("2")


# 자녀가 있으면 자녀를 추가하기!
child_insur = []
if int(child) == 1:
    child_insur = ['(무)온라인어린이']

# 패키지들 조합하기
wb = pd.read_excel('D:\Hackerthon_result\insur_cost.xlsx')
df = pd.DataFrame(wb)

print(insurance_list)

d = []
cost_list = []

# 구현 못한 것 - 전체 조합 다 확인
# 현재 - 2개와 3개 보험 조합만 확인

for i in [2,3]: #range(1, len(insurance_list)):
    sets = itertools.combinations(insurance_list,i)    
    
    for subset in sets:
        sum_subset = 0
        for s in subset:
            if int(age) <= 39:
                if gender == 1:
                    sum_subset += int(df[df.iloc[:,0] == s].iloc[:,1])
                elif gender == 2:
                    sum_subset += int(df[df.iloc[:,0] == s].iloc[:,3])
            elif 40 < int(age) <= 49:
                if gender == 1:
                    sum_subset += int(df[df.iloc[:,0] == s].iloc[:,2])
                elif gender == 2:
                    sum_subset += int(df[df.iloc[:,0] == s].iloc[:,4])

        if sum_subset < up_limit:
            d += [list(subset) + child_insur]
            cost_list += [sum_subset]

print(d)
print(len(d))

# 제일 패키지 총합 금액이 적은 순으로 정렬
l = [(x,y) for x,y in zip(d, cost_list)]
fff = sorted(l, key=lambda x:x[1])
res = [x[0] for x in fff][:5]

f = open("insurance_recommend_list.json", "wt")
json.dump(res, f)
f.close()

print(res)

# 구현 못한 것 - 들어간 보험 개수로 나눠서 평균 금액으로 순차적 배열
# 현재 - 전체 금액으로 순차적 배열

# 구현 못한 것 - 보장 범위가 겹치는 거 따로 외부 파일 불러와서 빼기
# 현재 - 애초에 input을 보장 범위 겹치는 건 최소 금액인 애로만 넣음

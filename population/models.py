from common.models import FileDTO, Reader, Printer
import pandas as pd


'''
65세 이상 노인 인구와 20∼39세 여성 인구를 비교해 젊은 여성 인구가 
노인 인구의 절반에 미달할 경우 ‘소멸 위험 지역’으로 분류하는 방식'''

class Service(Reader):

    def __init__(self):
        self.f = FileDTO()
        self.r = Reader()
        self.p = Printer()


    def save_pop(self):
        f = self.f
        r = self.r
        p = self.p
        f.context = './data/'
        f.fname = '05. population_raw_data'
        draw_korea = r.xls(f, 1, None)
        #p.dframe(draw_korea)
        draw_korea.fillna(method='pad',inplace=True)
        draw_korea.rename(columns={
            '행정구역(동읍면)별(1)': '광역시도',
            '행정구역(동읍면)별(2)': '시도',
            '계': '인구수'}, inplace=True)
        draw_korea = draw_korea[(draw_korea['시도'] != '소계')]
        #시구 컬럼이 소계 + 용산구 이런식으로 되어 있어서 소계는 제외한 시도를 뽑기 위한 코드
        # print(draw_korea)
        draw_korea.is_copy = False
        draw_korea.rename(columns = {'항목':'구분'}, inplace=True)
        draw_korea.loc[draw_korea['구분'] == '총인구수 (명)', '구분'] = '합계'
        # print(type(draw_korea['구분']) = <class 'pandas.core.series.Series'> )
        draw_korea.loc[draw_korea['구분'] == '남자인구수 (명)', '구분'] = '남자'
        draw_korea.loc[draw_korea['구분'] == '여자인구수 (명)', '구분'] = '여자'
        # print(draw_korea)

        draw_korea['20-39세'] = draw_korea['20 - 24세'] + draw_korea['25 - 29세'] \
                              + draw_korea['30 - 34세'] + draw_korea['35 - 39세']

        draw_korea['65세이상'] = draw_korea['65 - 69세'] + draw_korea['70 - 74세'] \
                               + draw_korea['75 - 79세'] + draw_korea['80 - 84세'] \
                               + draw_korea['85 - 89세'] + draw_korea['90 - 94세'] \
                               + draw_korea['95 - 99세'] + draw_korea['100+']
        # print(draw_korea)

        pop = pd.pivot_table(draw_korea, index=['광역시도', '시도'], columns=['구분'], values=['인구수', '20-39세', '65세이상'])
        # print(pop)
        pop['소멸비율'] = pop['20-39세','여자'] / (pop['65세이상','합계'] / 2)
        # print(pop.head())
        pop['소멸위기지역'] = pop['소멸비율'] < 1.0
        #print(pop.head())
        #.index.get_level_values(1) 멀티인덱스에서 특정 레벨(단계)의 레이블을 추출해야하는경우 = 벡터반환
        pop[pop['소멸위기지역']==True].index.get_level_values(1)

        pop.reset_index(inplace=True) # 0,1,2 .. 를인덱스로 추가하고 기존인덱스는 1열이 된다
        # print(pop.head())

        tmp_columns = [pop.columns.get_level_values(0)[n] + pop.columns.get_level_values(1)[n]
                        for n in range(0, len(pop.columns.get_level_values(0)))]
        pop.columns=tmp_columns
        # print(pop.head())
        pop['시도'].unique()
        # print(pop['시도'].unique())
        si_name = [None] * len(pop)
        #print(si_name)
        # 시도 칼럼에서 시 안에 포함된 구 가 값이 크기 떄문에 따로 빠져나온 경우로 인해서 아래와 같이 따로 만들어줌
        # 예를 들어 청주시의 경우 상당구 서원구가 시도 칼럼에 같이 존재 하기때문이다
        tmp_gu_dict = {'수원':['장안구', '권선구', '팔달구', '영통구'],
                       '성남':['수정구', '중원구', '분당구'],
                       '안양':['만안구', '동안구'],
                       '안산':['상록구', '단원구'],
                       '고양':['덕양구', '일산동구', '일산서구'],
                       '용인':['처인구', '기흥구', '수지구'],
                       '청주':['상당구', '서원구', '흥덕구', '청원구'],
                       '천안':['동남구', '서북구'],
                       '전주':['완산구', '덕진구'],
                       '포항':['남구', '북구'],
                       '창원':['의창구', '성산구', '진해구', '마산합포구', '마산회원구'],
                       '부천':['오정구', '원미구', '소사구']}


        for n in pop.index:
            if pop['광역시도'][n]:
                pass



if __name__ == '__main__':
    s = Service()
    s.save_pop()



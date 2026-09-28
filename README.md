# HRDKorea Public Data Skill

한국산업인력공단(한국산업인력개발원) 공공데이터 MCP 서버를 조회하는 에이전트 스킬입니다.
`openapi.hrdkorea.or.kr/mcp` 엔드포인트에 노출된 **45개 읽기 전용 조회 도구**를 활용하여 국가자격시험, 경력 로드맵, 해외취업, NCS, 과정평가형·일학습병행, 대한민국명장, 외국인고용(EPS) 데이터를 검색합니다.

인증 키가 필요 없으며, 모든 도구는 읽기 전용 조회입니다.

## 구성

```
hrdk-public-data/
├── SKILL.md              # 스킬 설명서 (트리거 조건·호출 방법·도메인별 도구 매핑표)
├── scripts/
│   └── call.py           # MCP 서버 호출 헬퍼 (핸드셰이크·SSE 파싱 자동 처리)
└── references/
    ├── tools.md          # 45개 도구 전체 매뉴얼 (파라미터명·타입·필수 여부)
    └── tools_raw.txt     # 서버에서 받은 원시 도구 목록 (검증용)
```

## 사용법

스킬 폴더로 이동한 뒤 헬퍼 스크립트로 도구를 호출합니다.

```bash
cd skills/hrdk-public-data

# 자격증 검색
python3 scripts/call.py search_qualification '{"query": "전기"}'

# 시험 일정 (종목코드 불필요)
python3 scripts/call.py get_exam_schedule '{"qualificationName": "정보처리기사"}'

# 응시수수료
python3 scripts/call.py get_exam_fee '{"qualificationName": "정보처리기사"}'

# 경력 기반 자격 추천
python3 scripts/call.py recommend_qualifications '{"careerQuery": "시설관리 경력 5년"}'

# 전체 도구 + JSON 스키마 확인
python3 scripts/call.py list-tools
```

`call.py`는 MCP 핸드셰이크(initialize → initialized → tools/call)와 SSE 응답 파싱을 자동으로 처리합니다.

## 지원 도메인

| 도메인 | 주요 기능 |
|---|---|
| **HRDK 역량 내비게이터** | 경력 기반 자격 추천, 커리어 로드맵, 법정 선임요건 검토 |
| **국가자격시험 (Q-Net)** | 종목 검색, 시험 일정, 상세정보, 응시수수료, 합격률, 시험장, 결격사유, 기출문제 |
| **해외취업 (월드잡플러스)** | 채용공고, 우수일자리, 취업 통계, 구인기업, 설명회, K-Move, 정착지원금 |
| **NCS 국가직무능력표준** | 능력단위 검색, 분류체계, 연계 자격, 학습자료, 블라인드 채용, 직업기초능력 |
| **과정평가형·일학습병행** | 무시험 자격, 일학습병행 종목, 훈련 기관·기업, 외부평가 시험장·통계 |
| **숙련기술 (대한민국명장)** | 명장 검색·통계, 작품전시관, 기능경기·산업현장교수 통계 |
| **외국인고용 (EPS)** | EPS-TOPIK 일정·시험장·교재, 외국인 구직자, 귀국지원, 취업교육 |

전체 파라미터 세부사항은 [`references/tools.md`](references/tools.md)를 참고하세요.

## 참고

- 자격증·종목 이름은 정확하지 않아도 퍼지 매칭으로 해석되며, 모호하면 서버가 후보를 되묻습니다.
- 일부 도구(예: `search_ncs`)는 첫 호출 시 데이터 수집 때문에 느릴 수 있습니다(최대 ~120초).
- 결과가 URL(Q-Net 페이지, 가이드북 PDF 등)을 포함하면 그대로 Markdown 링크로 제시합니다.

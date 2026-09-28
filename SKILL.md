---
name: hrdk-public-data
description: Query the Korea HRDKorea (한국산업인력공단) public-data MCP server at openapi.hrdkorea.or.kr/mcp for national qualification exam info, career roadmaps, overseas jobs, NCS competencies, dual training programs, master craftsmen, and EPS foreign worker data. Use this skill whenever the user asks about 자격증/국가자격 (qualification certificates), 시험 일정/응시료/합격률/기출문제 (exam schedules, fees, pass rates, past questions), 해외취업/해외채용 (overseas employment), NCS 능력단위 (NCS competency units), 과정평가형/일학습병행 (course-based or work-learning qualifications), 대한민국명장 (master craftsmen), EPS-TOPIK/외국인고용 (foreign worker hiring), or wants a career roadmap tied to legal appointment requirements. Trigger even when the user doesn't mention "HRD" or "Q-Net" — any question about Korean vocational qualifications, exams, or workforce statistics should use this skill. All queries are read-only lookups; no API key is required.
---

# HRDKorea Public Data Skill

Query the 한국산업인력공단 (Korea Human Resource Development Corporation) public-data MCP server. The server exposes 45 read-only lookup tools covering national qualifications, career navigation, overseas employment, NCS standards, dual training, master craftsmen, and foreign worker hiring. No authentication is needed.

## How to call a tool

Use the bundled helper script. It handles the MCP handshake (initialize → initialized → tools/call) and parses the SSE response automatically.

```bash
python3 scripts/call.py <tool_name> '<json_arguments>'
```

Examples:

```bash
# Search qualification certificates by keyword
python3 scripts/call.py search_qualification '{"query": "전기"}'

# Get exam schedule for a qualification (no item code needed)
python3 scripts/call.py get_exam_schedule '{"qualificationName": "정보처리기사"}'

# Recommend qualifications from a career description
python3 scripts/call.py recommend_qualifications '{"careerQuery": "시설관리 경력 5년"}'

# List all tools with their JSON schemas (if unsure of parameter names)
python3 scripts/call.py list-tools
```

Run the script from the skill directory (`cd` into it first) so the relative path resolves. If `list-tools` output is stale or you need exact parameter names, run it again — it always reflects the live server.

## Workflow

1. **Identify the domain** from the user's request using the table below.
2. **Read the matching section** in `references/tools.md` to get the exact tool name and parameter names/types. Do not guess parameter names — they vary per tool (e.g., `keyword` vs `qualification_name` vs `careerQuery`).
3. **Call the tool** via `scripts/call.py`. Pass arguments as a single JSON string.
4. **Present results** clearly. For lists/statistics, format as a Markdown table. For schedules, show dates prominently. Cite that the source is 한국산업인력공단 공공데이터.

If the server returns an ambiguity message (it fuzzy-matches names and asks back when unclear), relay the candidates to the user and ask which one they meant, then re-call with the exact name.

## Domain → tool quick map

| User intent | Tool(s) |
|---|---|
| 자격증 검색 / 종목 찾기 | `search_qualification` |
| 시험 일정 (접수·필기·실기·발표) | `get_exam_schedule` |
| 자격 상세정보 (직무·진로·전망) | `get_qualification_info` |
| 응시수수료 | `get_exam_fee` |
| 합격률·통계 | `get_pass_rate` |
| 지역별 시험장 | `find_test_sites` |
| 결격사유·유사종목 | `get_disqualification_info` |
| 기출문제 공고 | `get_exam_questions` |
| 경력 기반 자격 추천 | `recommend_qualifications` |
| 커리어 로드맵 + 법정 선임요건 | `build_career_roadmap`, `check_legal_requirements` |
| 해외 채용공고 | `search_overseas_jobs`, `search_overseas_top_jobs` |
| 해외 취업 통계 | `get_overseas_employment_stats` |
| 해외 구인기업 | `search_overseas_companies`, `get_overseas_hiring_stats` |
| 해외 설명회·아카데미 | `get_overseas_job_fairs` |
| 국가별 비자·진출 정보 | `get_overseas_country_info` |
| 정착지원금 실적 | `get_overseas_settlement_support` |
| K-Move 연수·인턴 | `search_kmove_programs` |
| NCS 능력단위 검색 | `search_ncs` |
| 능력단위 ↔ 연계 자격 | `get_ncs_related_qualifications` |
| NCS 학습자료 | `search_ncs_learning_materials` |
| 블라인드 채용 공고 | `search_blind_hiring` |
| 직업기초능력 | `get_ncs_core_competencies` |
| NCS 분류체계 | `get_ncs_classification` |
| 과정평가형 자격 | `search_course_qualifications` |
| 일학습병행 종목 | `search_work_learning_qualifications` |
| 훈련 기관·기업 | `search_dual_training_orgs` |
| 외부평가 시험장·수수료·통계 | `find_dual_exam_sites`, `get_dual_exam_fee`, `get_dual_exam_stats` |
| 기업 훈련 통계 | `get_industry_training_stats` |
| 대한민국명장 검색·통계·작품 | `search_master_craftsmen`, `get_master_stats`, `search_master_artworks` |
| 기능경기·산업현장교수 통계 | `get_skill_stats` |
| EPS-TOPIK 일정·시험장·교재 | `get_eps_topik_schedule`, `find_eps_topik_sites`, `get_eps_topik_materials` |
| 외국인 구직자 검색 | `search_eps_jobseekers` |
| 귀국지원 통계·현지 일자리 | `get_eps_return_support_stats`, `search_eps_return_jobs` |
| 외국인 취업교육 | `get_eps_education_info` |

Full parameter details for every tool are in `references/tools.md`.

## Notes

- All tools are read-only; calling them never writes or submits anything.
- Qualification/item names don't need to be exact — the server fuzzy-matches and will ask back if ambiguous.
- Some tools (e.g., `search_ncs`) may be slow on first call due to data collection; allow up to ~120s.
- When a result includes URLs (e.g., Q-Net pages, guidebook PDFs), present them verbatim as Markdown links.

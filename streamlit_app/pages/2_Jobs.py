"""Job listings page — browse, filter, and apply to jobs.
Drop-in replacement: uses ht_components for branded visuals.
"""
from __future__ import annotations

import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import streamlit as st
from utils import JOB_TYPE_LABELS, api_get, api_post, cold_start_guard
from ht_components import (
    inject_global_css, page_header, section_header,
    job_card_html, info_box, kpi_row, HT_COLORS,
)

st.set_page_config(
    page_title="Job Board · HireTrack AI",
    page_icon="💼",
    layout="wide",
)
inject_global_css()
cold_start_guard()
page_header("Job Board", "Browse and apply to curated opportunities.")

# ── Demo data seeder ──────────────────────────────────────────────────────────
DEMO_JOBS = [
    {"title":"Senior Backend Engineer","company":"TechNova Inc","url":"https://technova.io/jobs/sbe","location":"San Francisco, CA","description":"TechNova is seeking a Senior Backend Engineer to design and maintain high-throughput APIs. You will own core services written in Python and FastAPI, optimize PostgreSQL queries, and lead code reviews.\n\nResponsibilities:\n• Design RESTful and GraphQL APIs serving 10M+ daily requests\n• Optimize database schemas and query performance\n• Mentor junior engineers and conduct code reviews\n• Collaborate with frontend and DevOps teams\n• Drive architectural decisions for new features\n\nRequirements:\n• 5+ years backend development experience\n• Expert-level Python (FastAPI, SQLAlchemy)\n• Strong SQL and PostgreSQL knowledge\n• Experience with Docker and AWS\n• Familiarity with Redis and message queues\n\nBenefits: Health/dental/vision, 401k matching, remote-first, $150k-$190k base.","job_type":"full_time","remote":True,"salary_range":"$150,000 – $190,000","experience_level":"senior","skills_required":{"required":["Python","FastAPI","PostgreSQL","Docker","AWS","Redis"],"preferred":["Kubernetes","GraphQL","Kafka"]}},
    {"title":"React Frontend Engineer","company":"PixelCraft Studios","url":"https://pixelcraft.io/careers/fe","location":"New York, NY","description":"PixelCraft Studios builds design-forward SaaS products. We need a skilled React engineer to own our frontend experience.\n\nResponsibilities:\n• Build pixel-perfect UIs from Figma designs\n• Implement state management with Zustand and React Query\n• Write unit and integration tests with Vitest and Playwright\n• Optimize Core Web Vitals and page load performance\n• Collaborate closely with designers and backend engineers\n\nRequirements:\n• 3+ years React experience\n• Strong TypeScript skills\n• Proficiency with CSS-in-JS and Tailwind CSS\n• Experience with REST and GraphQL APIs\n• Familiarity with Storybook and design systems\n\nBenefits: Hybrid NYC office, $120k-$160k, generous PTO, learning budget.","job_type":"full_time","remote":False,"salary_range":"$120,000 – $160,000","experience_level":"mid","skills_required":{"required":["React","TypeScript","CSS","HTML","REST APIs"],"preferred":["GraphQL","Tailwind CSS","Playwright","Zustand"]}},
    {"title":"Senior Data Scientist","company":"DataMinds Analytics","url":"https://dataminds.ai/jobs/ds","location":"Austin, TX","description":"DataMinds helps enterprises turn raw data into strategic insights. Join our data science team to build predictive models and recommendation engines.\n\nResponsibilities:\n• Develop and deploy ML models for churn prediction and LTV estimation\n• Build ETL pipelines and feature stores\n• Collaborate with business stakeholders to define KPIs\n• Present findings to C-suite executives\n• Own model monitoring and retraining pipelines\n\nRequirements:\n• 4+ years data science experience\n• Expert Python (pandas, scikit-learn, XGBoost)\n• Strong statistics and probability knowledge\n• Experience with SQL and data warehouses (BigQuery/Redshift)\n• Familiarity with MLflow or similar experiment tracking\n\nBenefits: Remote-first, $130k-$170k, equity, conference budget.","job_type":"full_time","remote":True,"salary_range":"$130,000 – $170,000","experience_level":"senior","skills_required":{"required":["Python","Machine Learning","SQL","pandas","scikit-learn","Statistics"],"preferred":["XGBoost","MLflow","BigQuery","Spark"]}},
    {"title":"DevOps / Platform Engineer","company":"CloudPeak Systems","url":"https://cloudpeak.io/careers/devops","location":"Seattle, WA","description":"CloudPeak Systems builds cloud infrastructure for Fortune 500 clients. We need a DevOps engineer to own CI/CD pipelines and Kubernetes clusters.\n\nResponsibilities:\n• Design and maintain Kubernetes clusters on AWS EKS\n• Build and optimize CI/CD pipelines with GitHub Actions and ArgoCD\n• Implement infrastructure as code using Terraform\n• Monitor systems with Prometheus, Grafana, and PagerDuty\n• Drive security best practices and compliance\n\nRequirements:\n• 4+ years DevOps/platform engineering experience\n• Expert-level Kubernetes and Docker\n• Strong Terraform and AWS knowledge\n• Experience with GitHub Actions or similar CI/CD tools\n• Scripting skills in Bash and Python\n\nBenefits: Remote, $140k-$180k, AWS certification reimbursement.","job_type":"full_time","remote":True,"salary_range":"$140,000 – $180,000","experience_level":"senior","skills_required":{"required":["Kubernetes","Docker","AWS","Terraform","CI/CD","Linux"],"preferred":["ArgoCD","Prometheus","Grafana","Helm"]}},
    {"title":"Full Stack Engineer","company":"Velocity Startup","url":"https://velocityhq.com/jobs/fse","location":"Remote","description":"Velocity is a fast-growing B2B SaaS startup. We are looking for a full-stack engineer who thrives in ambiguity and can ship features end-to-end.\n\nResponsibilities:\n• Build features across the React frontend and Node.js backend\n• Design and maintain PostgreSQL schemas\n• Write automated tests and participate in code reviews\n• Deploy and monitor services on AWS\n• Contribute to architectural discussions\n\nRequirements:\n• 3+ years full-stack development\n• Proficiency in React and Node.js\n• Strong SQL skills\n• Experience with REST API design\n• Comfortable with Git workflows and Agile sprints\n\nBenefits: Fully remote, $100k-$140k, startup equity, unlimited PTO.","job_type":"full_time","remote":True,"salary_range":"$100,000 – $140,000","experience_level":"mid","skills_required":{"required":["React","Node.js","JavaScript","PostgreSQL","REST APIs","Git"],"preferred":["TypeScript","AWS","Docker","GraphQL"]}},
    {"title":"Machine Learning Engineer","company":"AI Ventures","url":"https://aiventures.com/careers/mle","location":"Boston, MA","description":"AI Ventures is at the frontier of applied AI. Join our ML engineering team to build production ML systems at scale.\n\nResponsibilities:\n• Train and fine-tune large language models and computer vision models\n• Build scalable model serving infrastructure with TorchServe and FastAPI\n• Implement data pipelines for training and evaluation\n• Collaborate with research scientists to productionize models\n• Optimize inference latency and throughput\n\nRequirements:\n• 4+ years ML engineering experience\n• Expert PyTorch or TensorFlow skills\n• Experience with distributed training (FSDP, DeepSpeed)\n• Strong Python and software engineering fundamentals\n• Familiarity with MLOps tools (MLflow, Weights & Biases)\n\nBenefits: On-site Boston, $160k-$210k, significant equity.","job_type":"full_time","remote":False,"salary_range":"$160,000 – $210,000","experience_level":"senior","skills_required":{"required":["Python","PyTorch","Machine Learning","Deep Learning","MLOps"],"preferred":["TensorFlow","CUDA","Kubernetes","MLflow","LLMs"]}},
    {"title":"Senior Product Manager","company":"GrowthCo","url":"https://growthco.com/pm","location":"New York, NY","description":"GrowthCo helps e-commerce brands scale with AI-powered growth tools. We need a technical PM to own our analytics product line.\n\nResponsibilities:\n• Define product roadmap and quarterly OKRs for analytics suite\n• Work with engineering to size and prioritize features\n• Conduct user research and synthesize insights\n• Write detailed PRDs and acceptance criteria\n• Track product metrics and drive growth experiments\n\nRequirements:\n• 5+ years product management experience (SaaS preferred)\n• Technical background — comfortable reading code and APIs\n• Strong data analysis skills (SQL, Mixpanel, Amplitude)\n• Excellent communication and stakeholder management\n• Experience running A/B tests and feature flags\n\nBenefits: Hybrid NYC, $140k-$180k plus bonus and equity.","job_type":"full_time","remote":False,"salary_range":"$140,000 – $180,000","experience_level":"senior","skills_required":{"required":["Product Management","SQL","Data Analysis","Agile","User Research"],"preferred":["A/B Testing","Mixpanel","JIRA","Figma"]}},
    {"title":"Junior Software Engineer","company":"DevFactory","url":"https://devfactory.com/junior","location":"Chicago, IL","description":"DevFactory builds enterprise workflow software. We are hiring junior engineers eager to learn and grow within a supportive team.\n\nResponsibilities:\n• Implement features in Python and Django under senior guidance\n• Write unit tests and participate in code reviews\n• Fix bugs and improve documentation\n• Participate in sprint planning and retrospectives\n• Learn codebase patterns and best practices\n\nRequirements:\n• 0–2 years professional software development experience\n• Solid Python fundamentals\n• Basic understanding of SQL and web development\n• Familiarity with Git version control\n• CS degree or equivalent bootcamp/self-taught background\n\nBenefits: On-site Chicago, $80k-$110k, structured mentorship programme.","job_type":"full_time","remote":False,"salary_range":"$80,000 – $110,000","experience_level":"junior","skills_required":{"required":["Python","SQL","Git","HTML","CSS"],"preferred":["Django","REST APIs","Docker","JavaScript"]}},
    {"title":"QA Automation Engineer","company":"QualityFirst Tech","url":"https://qualityfirst.tech/qa","location":"Austin, TX","description":"QualityFirst Tech delivers SaaS quality management tools. We need a QA engineer to build and maintain our automated test suite.\n\nResponsibilities:\n• Design and implement end-to-end test automation using Playwright and Pytest\n• Maintain CI/CD integration for automated tests\n• Perform API testing with Postman and custom scripts\n• Track defects and work closely with developers\n• Improve test coverage and reporting dashboards\n\nRequirements:\n• 3+ years QA automation experience\n• Proficiency with Playwright, Selenium, or Cypress\n• Strong Python or JavaScript scripting skills\n• Experience with REST API testing\n• Understanding of CI/CD pipelines\n\nBenefits: Remote, $90k-$120k, flexible hours.","job_type":"full_time","remote":True,"salary_range":"$90,000 – $120,000","experience_level":"mid","skills_required":{"required":["Test Automation","Playwright","Python","API Testing","CI/CD"],"preferred":["Selenium","Cypress","Postman","JIRA","Pytest"]}},
    {"title":"Site Reliability Engineer","company":"InfraMax","url":"https://inframax.io/sre","location":"San Francisco, CA","description":"InfraMax provides infrastructure management for high-scale web applications. Join our SRE team to keep systems fast and reliable.\n\nResponsibilities:\n• Define and enforce SLOs, SLIs, and error budgets\n• Build and maintain observability stack (Prometheus, Grafana, Jaeger)\n• Automate incident response and runbooks\n• Conduct blameless post-mortems\n• Collaborate with development teams on production readiness reviews\n\nRequirements:\n• 5+ years SRE or systems engineering experience\n• Expert Linux administration skills\n• Strong Kubernetes and Docker knowledge\n• Proficiency in Go or Python for tooling\n• Experience with incident management (PagerDuty, OpsGenie)\n\nBenefits: Remote-first, $160k-$200k, on-call allowance.","job_type":"full_time","remote":True,"salary_range":"$160,000 – $200,000","experience_level":"senior","skills_required":{"required":["Kubernetes","Linux","Python","Go","Prometheus","Grafana","Docker"],"preferred":["Terraform","Jaeger","PagerDuty","AWS","SLO/SLI"]}},
    {"title":"Android Developer","company":"MobileFirst Corp","url":"https://mobilefirst.io/android","location":"Los Angeles, CA","description":"MobileFirst Corp builds consumer mobile apps with 5M+ active users. We need an Android developer to own core app features.\n\nResponsibilities:\n• Build and maintain features in Kotlin and Jetpack Compose\n• Integrate REST APIs and manage offline state with Room\n• Write unit and UI tests with JUnit and Espresso\n• Optimize app performance and battery usage\n• Publish releases through Google Play Console\n\nRequirements:\n• 3+ years Android development experience\n• Strong Kotlin skills and Jetpack Compose knowledge\n• Experience with MVVM architecture and Coroutines\n• Familiarity with REST API integration and JSON parsing\n• Published apps on Google Play preferred\n\nBenefits: Hybrid LA, $120k-$160k, device budget.","job_type":"full_time","remote":False,"salary_range":"$120,000 – $160,000","experience_level":"mid","skills_required":{"required":["Kotlin","Android","Jetpack Compose","REST APIs","MVVM","Coroutines"],"preferred":["Room","Hilt","Firebase","CI/CD","Java"]}},
    {"title":"iOS Developer","company":"AppWorks Studio","url":"https://appworks.studio/ios","location":"San Francisco, CA","description":"AppWorks Studio crafts premium iOS applications for enterprise clients. We are looking for an iOS developer with a passion for clean code and great UX.\n\nResponsibilities:\n• Build and maintain iOS apps in Swift and SwiftUI\n• Integrate REST APIs and handle complex async flows with Combine/async-await\n• Write unit and snapshot tests with XCTest\n• Collaborate with designers to implement pixel-perfect UIs\n• Support App Store releases and beta testing with TestFlight\n\nRequirements:\n• 3+ years iOS development experience\n• Proficiency in Swift and SwiftUI\n• Understanding of iOS architecture patterns (MVVM, Clean Architecture)\n• Experience with Xcode and Instruments for performance profiling\n• Knowledge of Apple Human Interface Guidelines\n\nBenefits: Remote, $130k-$170k, MacBook Pro provided.","job_type":"full_time","remote":True,"salary_range":"$130,000 – $170,000","experience_level":"mid","skills_required":{"required":["Swift","SwiftUI","iOS","Xcode","REST APIs","MVVM"],"preferred":["Combine","CoreData","Firebase","TestFlight","Objective-C"]}},
    {"title":"Senior Data Engineer","company":"DataFlow Inc","url":"https://dataflow.inc/data-eng","location":"Seattle, WA","description":"DataFlow Inc builds the data infrastructure for mid-market companies. We need a senior data engineer to design and maintain our lakehouse platform.\n\nResponsibilities:\n• Build and maintain ELT pipelines using Apache Spark and dbt\n• Design data models in Snowflake and manage schema migrations\n• Orchestrate workflows with Apache Airflow\n• Implement data quality checks and monitoring\n• Mentor junior data engineers\n\nRequirements:\n• 5+ years data engineering experience\n• Expert Apache Spark and SQL skills\n• Strong experience with dbt and data modeling\n• Proficiency with cloud data warehouses (Snowflake, BigQuery, or Redshift)\n• Experience with workflow orchestration (Airflow, Prefect, or Dagster)\n\nBenefits: Remote, $140k-$180k, equity, annual learning stipend.","job_type":"full_time","remote":True,"salary_range":"$140,000 – $180,000","experience_level":"senior","skills_required":{"required":["Apache Spark","SQL","dbt","Airflow","Python","Snowflake"],"preferred":["Kafka","BigQuery","Delta Lake","Terraform","Scala"]}},
    {"title":"Application Security Engineer","company":"SecureNet","url":"https://securenet.io/appsec","location":"Washington, DC","description":"SecureNet provides cybersecurity services to government and enterprise clients. Join our application security team to harden products against modern threats.\n\nResponsibilities:\n• Perform threat modelling and secure code reviews\n• Conduct DAST and SAST scanning and triage findings\n• Build and maintain security automation in CI/CD pipelines\n• Develop security training for development teams\n• Respond to and investigate security incidents\n\nRequirements:\n• 4+ years application security experience\n• Deep knowledge of OWASP Top 10 and secure coding practices\n• Experience with SAST/DAST tools (Semgrep, Burp Suite, OWASP ZAP)\n• Programming skills in Python or Go\n• Security certifications (OSCP, CISSP, or CEH) preferred\n\nBenefits: On-site DC (clearance eligible), $150k-$190k.","job_type":"full_time","remote":False,"salary_range":"$150,000 – $190,000","experience_level":"senior","skills_required":{"required":["Application Security","OWASP","Python","Penetration Testing","CI/CD","SAST/DAST"],"preferred":["Burp Suite","Semgrep","Go","AWS Security","OSCP"]}},
    {"title":"Backend Engineer (Go)","company":"DistributedSys","url":"https://distributedsys.io/go-eng","location":"Remote","description":"DistributedSys builds distributed systems infrastructure used by thousands of developers. We need a backend engineer specialising in Go to help scale our platform.\n\nResponsibilities:\n• Build high-performance microservices in Go with gRPC and REST\n• Design distributed data structures and consensus algorithms\n• Optimize service latency and throughput at scale\n• Write comprehensive unit and integration tests\n• Participate in on-call rotation and incident response\n\nRequirements:\n• 3+ years Go development experience\n• Strong understanding of concurrency patterns in Go\n• Experience with gRPC and Protocol Buffers\n• Familiarity with distributed systems concepts (CAP theorem, consensus, CRDT)\n• Comfortable with Linux systems programming\n\nBenefits: Fully remote, $130k-$170k, async-first culture.","job_type":"full_time","remote":True,"salary_range":"$130,000 – $170,000","experience_level":"mid","skills_required":{"required":["Go","gRPC","REST APIs","Distributed Systems","Linux","Docker"],"preferred":["Kubernetes","Protocol Buffers","PostgreSQL","Redis","Kafka"]}},
    {"title":"NLP / AI Research Scientist","company":"LanguageAI Labs","url":"https://languageai.io/research","location":"Boston, MA","description":"LanguageAI Labs is a research-led company building next-generation language models. Join our research team to push the boundaries of NLP.\n\nResponsibilities:\n• Design and conduct experiments on large language models\n• Fine-tune and evaluate models on domain-specific tasks\n• Publish research findings at top NLP venues (ACL, EMNLP, NeurIPS)\n• Collaborate with engineering to productionise research breakthroughs\n• Stay current with state-of-the-art NLP literature\n\nRequirements:\n• PhD or MS in Computer Science, NLP, or related field\n• Deep expertise in transformer architectures and LLMs\n• Strong PyTorch and HuggingFace Transformers skills\n• Publication record at top ML/NLP conferences\n• Proficiency in Python and scientific computing stack\n\nBenefits: Hybrid Boston, $180k-$250k, significant research compute budget.","job_type":"full_time","remote":False,"salary_range":"$180,000 – $250,000","experience_level":"senior","skills_required":{"required":["NLP","LLMs","PyTorch","Python","Transformers","Research"],"preferred":["HuggingFace","RLHF","CUDA","JAX","Academic Publishing"]}},
    {"title":"Principal Cloud Architect","company":"CloudArch Solutions","url":"https://cloudarch.io/principal","location":"Remote","description":"CloudArch Solutions designs and implements cloud strategies for enterprise clients across industries. We need a principal architect to lead multi-cloud engagements.\n\nResponsibilities:\n• Lead architecture design for complex multi-cloud migrations\n• Define cloud standards, guardrails, and reference architectures\n• Advise clients on cost optimisation and security posture\n• Mentor a team of cloud engineers\n• Produce architecture decision records and technical roadmaps\n\nRequirements:\n• 8+ years cloud engineering and architecture experience\n• Expert knowledge of AWS, Azure, or GCP (multi-cloud preferred)\n• Strong Terraform and infrastructure-as-code skills\n• Experience with enterprise networking (VPCs, Direct Connect, ExpressRoute)\n• Professional cloud certifications (AWS Solutions Architect Professional, etc.)\n\nBenefits: Fully remote, $170k-$220k, travel reimbursement.","job_type":"full_time","remote":True,"salary_range":"$170,000 – $220,000","experience_level":"lead","skills_required":{"required":["AWS","Azure","GCP","Terraform","Cloud Architecture","Networking"],"preferred":["Kubernetes","Security","FinOps","CDK","Multi-cloud"]}},
    {"title":"Database Administrator","company":"DataGuard","url":"https://dataguard.io/dba","location":"Chicago, IL","description":"DataGuard provides managed database services to mid-size enterprises. We need a DBA to maintain and optimise our client database fleet.\n\nResponsibilities:\n• Administer and tune PostgreSQL and MongoDB clusters\n• Design backup and disaster recovery strategies\n• Monitor database performance and implement optimisations\n• Manage schema migrations and capacity planning\n• Support developers with query optimisation and index design\n\nRequirements:\n• 4+ years database administration experience\n• Expert PostgreSQL skills including replication and partitioning\n• Experience with MongoDB administration\n• Proficiency with database monitoring tools\n• Scripting skills in Bash or Python for automation\n\nBenefits: On-site Chicago, $110k-$145k, certification support.","job_type":"full_time","remote":False,"salary_range":"$110,000 – $145,000","experience_level":"mid","skills_required":{"required":["PostgreSQL","MongoDB","SQL","Database Administration","Backup/Recovery","Linux"],"preferred":["Redis","Elasticsearch","Python","Bash","AWS RDS"]}},
    {"title":"Software Engineering Intern","company":"TechStart","url":"https://techstart.io/internship","location":"Remote","description":"TechStart is a developer tools startup offering a 12-week paid summer internship. Interns work on real features alongside senior engineers.\n\nResponsibilities:\n• Implement features in Python or JavaScript under senior mentorship\n• Write unit tests and documentation\n• Participate in daily standups and weekly demos\n• Complete a capstone project presented to the team\n• Provide feedback on developer experience\n\nRequirements:\n• Currently enrolled in CS, Software Engineering, or related degree\n• Familiarity with at least one programming language (Python or JavaScript)\n• Basic understanding of Git\n• Eagerness to learn and receive feedback\n• Available for 12 weeks full-time\n\nBenefits: Fully remote, $35/hr-$45/hr, return offer consideration.","job_type":"internship","remote":True,"salary_range":"$35/hr – $45/hr","experience_level":"junior","skills_required":{"required":["Python","JavaScript","Git"],"preferred":["React","Django","Docker","SQL"]}},
    {"title":"Engineering Manager","company":"LeadTech Systems","url":"https://leadtech.io/em","location":"New York, NY","description":"LeadTech Systems builds B2B SaaS for the logistics industry. We need an engineering manager to lead a team of 8 engineers across backend and frontend.\n\nResponsibilities:\n• Manage, mentor, and grow a team of 6–8 software engineers\n• Drive technical roadmap and sprint planning\n• Collaborate with Product and Design on requirements\n• Own team hiring, performance reviews, and career development\n• Maintain high engineering quality and delivery predictability\n\nRequirements:\n• 3+ years engineering management experience\n• Strong technical background (6+ years hands-on software development)\n• Experience managing full-stack teams\n• Excellent communication and conflict resolution skills\n• Track record of shipping products on time\n\nBenefits: Hybrid NYC, $170k-$220k plus bonus and equity.","job_type":"full_time","remote":False,"salary_range":"$170,000 – $220,000","experience_level":"lead","skills_required":{"required":["Engineering Management","Leadership","Agile","Technical Roadmap","Hiring"],"preferred":["Python","React","AWS","System Design","OKRs"]}},
]

with st.expander("🌱 Load Demo Job Data", expanded=False):
    st.markdown(
        "Seed the database with **20 realistic job postings** to explore all features without a live job search.",
        unsafe_allow_html=False,
    )
    col_seed, col_info = st.columns([1, 2])
    with col_seed:
        if st.button("🚀 Create 20 Demo Jobs", type="primary", use_container_width=True):
            import time as _t
            progress = st.progress(0, text="Creating jobs…")
            created, failed = 0, 0
            for i, job in enumerate(DEMO_JOBS):
                res = api_post("/jobs/", job, silent=True)
                if res is None:
                    _t.sleep(1)           # brief pause then retry once
                    res = api_post("/jobs/", job, silent=True)
                if res:
                    created += 1
                else:
                    failed += 1
                progress.progress((i + 1) / len(DEMO_JOBS), text=f"Job {i+1}/{len(DEMO_JOBS)}…")
                _t.sleep(0.25)            # avoid overwhelming Render's DB pool
            progress.empty()
            if created:
                info_box(f"✅ Created {created} demo jobs! Refresh the page to see them.", kind="success")
            if failed:
                st.warning(
                    f"⚠️ **{failed} jobs failed.** "
                    "If the backend just woke up, wait 30 s and click again — already-existing jobs "
                    "are skipped automatically.",
                    icon="⚠️",
                )
    with col_info:
        info_box(
            "Includes roles across: Backend, Frontend, Data Science, ML, DevOps, SRE, "
            "Android, iOS, Security, QA, Product, and Management — all levels from Intern to Lead.",
            kind="info",
        )

# ── Filters ───────────────────────────────────────────────────────────────────
fc1, fc2, fc3, fc4, fc5 = st.columns([3, 1, 1, 1, 1])
with fc1:
    search_q = st.text_input(
        "",
        placeholder="🔍  Search by title, company, or skill…",
        label_visibility="collapsed",
    )
with fc2:
    remote_opt = st.selectbox(
        "Location",
        ["All", "Remote Only", "On-site Only"],
        label_visibility="collapsed",
    )
with fc3:
    jtype_opt = st.selectbox(
        "Job Type",
        ["All Types", "Full-time", "Part-time", "Contract"],
        label_visibility="collapsed",
    )
with fc4:
    exp_opt = st.selectbox(
        "Experience",
        ["All Levels", "Entry", "Junior", "Mid", "Senior", "Lead"],
        label_visibility="collapsed",
    )
with fc5:
    page_size = st.selectbox("Per page", [10, 20, 50], index=1, label_visibility="collapsed")

# ── Pagination state ──────────────────────────────────────────────────────────
if "jobs_page" not in st.session_state:
    st.session_state.jobs_page = 1

params: dict = {"page": st.session_state.jobs_page, "page_size": page_size}
if remote_opt == "Remote Only":
    params["remote"] = True
elif remote_opt == "On-site Only":
    params["remote"] = False

data      = api_get("/jobs/", params=params) or {}
all_items = data.get("items", [])
total     = data.get("total", 0)

# ── Client-side filtering ─────────────────────────────────────────────────────
items = all_items
if search_q:
    q     = search_q.lower()
    items = [
        j for j in items
        if q in j.get("title", "").lower()
        or q in j.get("company", "").lower()
        or q in j.get("description", "").lower()
        or any(q in s.lower() for s in (j.get("skills_required") or {}).get("required", []))
    ]
exp_map = {"Entry": "entry", "Junior": "junior", "Mid": "mid", "Senior": "senior", "Lead": "lead"}
if exp_opt in exp_map:
    items = [j for j in items if j.get("experience_level", "").lower() == exp_map[exp_opt]]

jtype_raw = {"Full-time": "full_time", "Part-time": "part_time", "Contract": "contract"}
if jtype_opt in jtype_raw:
    items = [j for j in items if j.get("job_type") == jtype_raw[jtype_opt]]

# ── Summary + pagination ──────────────────────────────────────────────────────
rc1, rc2, rc3 = st.columns([4, 1, 1])
rc1.markdown(
    f'<div style="font-size:13px;color:#64748B;padding:8px 0">'
    f'Showing <b style="color:#0F172A">{len(items)}</b> of '
    f'<b style="color:#0F172A">{total}</b> jobs</div>',
    unsafe_allow_html=True,
)
with rc2:
    if st.session_state.jobs_page > 1:
        if st.button("← Prev"):
            st.session_state.jobs_page -= 1
            st.rerun()
with rc3:
    if len(all_items) == page_size:
        if st.button("Next →"):
            st.session_state.jobs_page += 1
            st.rerun()

st.markdown(
    "<hr style='border:none;border-top:1px solid #E2E8F0;margin:6px 0 14px'>",
    unsafe_allow_html=True,
)

# ── Job cards ─────────────────────────────────────────────────────────────────
if not items:
    info_box("No jobs match your filters. Try broadening your search.", kind="info")
else:
    applied_ids: set = st.session_state.get("applied_job_ids", set())

    for job in items:
        posted  = job.get("posted_date")
        days_ago = ""
        if posted:
            try:
                dt       = datetime.fromisoformat(posted.replace("Z", "+00:00"))
                diff     = (datetime.now(timezone.utc) - dt).days
                days_ago = f"{diff}d ago" if diff > 1 else "Today"
            except Exception:
                pass

        match_score = job.get("match_score") or job.get("ats_score")
        if match_score and match_score <= 1.0:
            match_score = int(match_score * 100)

        st.markdown(
            job_card_html(job, match_score=match_score, applied=job["id"] in applied_ids),
            unsafe_allow_html=True,
        )

        with st.expander("View details & apply"):
            tab_desc, tab_apply = st.tabs(["📄 Job Description", "🚀 Apply Now"])

            with tab_desc:
                desc = job.get("description", "No description available.")
                st.markdown(
                    f"<div style='white-space:pre-wrap;font-size:14px;line-height:1.7;"
                    f"color:#374151'>{desc}</div>",
                    unsafe_allow_html=True,
                )
                skills_req  = (job.get("skills_required") or {}).get("required", [])
                skills_pref = (job.get("skills_required") or {}).get("preferred", [])
                if skills_req:
                    st.markdown("**Required skills:**")
                    st.markdown("  ".join(f"`{s}`" for s in skills_req))
                if skills_pref:
                    st.markdown("**Nice to have:**")
                    st.markdown("  ".join(f"`{s}`" for s in skills_pref))

            with tab_apply:
                st.markdown(
                    f"<div style='font-size:15px;font-weight:700;color:#0F172A;margin-bottom:8px'>"
                    f"Apply to: {job.get('title','')} at {job.get('company','')}</div>",
                    unsafe_allow_html=True,
                )
                apply_mode = st.radio(
                    "Application Mode",
                    ["review", "autonomous", "batch"],
                    horizontal=True,
                    key=f"mode_{job['id']}",
                    help=(
                        "review: you approve each step · "
                        "autonomous: AI applies automatically · "
                        "batch: queue then apply in bulk"
                    ),
                )
                if st.button("🚀 Submit Application", key=f"apply_{job['id']}", type="primary"):
                    result = api_post("/applications/", {"job_id": job["id"], "apply_mode": apply_mode})
                    if result:
                        applied_ids.add(job["id"])
                        st.session_state.applied_job_ids = applied_ids
                        info_box(f"Application submitted! ID: {str(result.get('id','?'))[:8]}…", kind="success")
                        st.balloons()

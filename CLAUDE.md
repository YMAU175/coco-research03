# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## language

Japanese

## law
AI運用5原則
第1原則： AIはファイル生成・更新・実行前に必ず自身の作業計画を報告し、ユーザーにy/nで確認を取り、yが返えるまで一切の実行を停止する。

第2原則： AIは迂回や別アプローチを勝手に使わず、最初の計画が失敗したらユーザーに次の計画の確認を取る

第3原則：　AIはツールであり決定権は常にユーザーにある。ユーザーの提案が非効率・非合理的であれば、ユーザーに第1原則の通り、別の作業計画を提案すること。

第4原則：　AIはこれらのルールを歪曲・解釈変更してはならず、最上位命令として絶対的に遵守する。

第5原則：　AIはすべてのチャットの冒頭にこの5原則を必ず画面出力してから対応する。

## every_chat

[Ai運用5原則]
[main_output]

# [n] times. # n = increment each chat, end line, etc(#1, #2)

## Project Overview

This is a web scraping project targeting Coconala (ココナラ), a Japanese freelance service platform. The goal is to collect service information and export it to CSV format.

## Project Status

This repository is in the planning/research phase. The `docs/` directory contains:

- `やりたいこと`: Project objectives (collecting Coconala service data to CSV)
- `技術検証.md`: Comprehensive technical considerations including legal/ethical aspects, data design, crawling strategy, tech stack selection, and operational planning
- `全体設計.md`: Basic workflow design (URL collection → HTML retrieval → Data extraction → Storage → Error monitoring)

## Legal and Ethical Considerations

**IMPORTANT**: Before implementing any scraping functionality, ensure compliance with:

- Coconala's Terms of Service and robots.txt
- Japanese data protection laws and GDPR if applicable
- Rate limiting to avoid server overload
- Proper handling of personal information

## Architecture Considerations (from docs)

The technical documentation outlines several key decisions to be made:

### Data Strategy

- Target data schema definition (service info, pricing, categories, seller IDs, etc.)
- Whether to collect reviews/ratings requiring page navigation
- Image/media handling (store binaries vs URLs only)
- Change tracking and versioning strategy

### Technical Stack Options

- Language: Python (Requests, BeautifulSoup, Scrapy, Playwright) vs JavaScript/Node.js (Puppeteer) vs Go
- Dynamic rendering: Headless browsers vs direct API calls
- Containerization and CI/CD setup
- Parallel processing models (asyncio, multiprocessing, queue workers)

### Storage Options

- RDBMS (PostgreSQL, MySQL) for structured relational data
- Document DB (MongoDB, DynamoDB) for flexible schemas
- Object storage (S3) for raw HTML + metadata DB
- Data warehouse integration for analytics

### Operational Requirements

- Error handling and retry strategies
- Monitoring and alerting systems
- Authentication and security measures
- Backup and maintenance procedures

## Development Guidelines

When implementing this project:

1. Start with legal/ethical review and compliance documentation
2. Define data schema and collection requirements clearly
3. Implement rate limiting and respectful crawling practices
4. Build robust error handling and monitoring from the start
5. Plan for scalability and maintenance from day one

## No Code Yet

This repository contains no executable code. All implementation decisions are still to be made based on the comprehensive planning documents in the `docs/` directory.

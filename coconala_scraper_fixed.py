#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ココナラ カテゴリランキングTOP10スクレイピングツール（修正版）
- 厳密な重複除去により正確な30日レビュー数を検出
- 同じ日付は1件のみカウント
"""

import requests
from bs4 import BeautifulSoup
import json
import pandas as pd
import time
import re
from urllib.parse import urljoin
from datetime import datetime, timedelta
import argparse

class CoconalaScraperFixed:
    
    def __init__(self, delay=2):
        self.delay = delay
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    def get_ranking_services(self, category_url, limit=10):
        """カテゴリページからランキングTOP10を正確に取得"""
        
        try:
            print(f"カテゴリページを取得中: {category_url}")
            response = self.session.get(category_url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # service_orderパラメータを持つURLを優先的に抽出
            ranking_services = []
            
            # service_order=1, 2, 3... を含むリンクを探す
            links = soup.find_all('a', href=lambda x: x and '/services/' in x and 'service_order=' in x)
            
            service_dict = {}  # 順位をキーにしたdict
            
            for link in links:
                href = link.get('href')
                # service_orderの値を抽出
                match = re.search(r'service_order=(\d+)', href)
                if match:
                    order = int(match.group(1))
                    url = urljoin('https://coconala.com', href)
                    clean_url = url.split('?')[0]
                    
                    # 同じ順位がなければ追加
                    if order not in service_dict:
                        service_dict[order] = clean_url
            
            # 順位順にソートして取得
            for i in range(1, limit + 1):
                if i in service_dict:
                    ranking_services.append(service_dict[i])
            
            # 不足分を補完（念のため）
            if len(ranking_services) < limit:
                all_links = soup.find_all('a', href=lambda x: x and '/services/' in x)
                for link in all_links:
                    url = urljoin('https://coconala.com', link.get('href'))
                    clean_url = url.split('?')[0]
                    if clean_url not in ranking_services and not clean_url.endswith('/add'):
                        ranking_services.append(clean_url)
                        if len(ranking_services) >= limit:
                            break
            
            return ranking_services[:limit]
            
        except Exception as e:
            print(f"カテゴリページ取得エラー: {e}")
            return []
    
    def extract_30day_reviews_fixed(self, soup, current_date):
        """修正版：30日以内のレビュー数を正確に抽出（厳密な重複除去）"""
        
        cutoff_date = current_date - timedelta(days=30)
        all_detected_reviews = []
        
        # 戦略1: メイン評価・感想セクション
        eval_results = self._extract_from_main_evaluation(soup, current_date)
        all_detected_reviews.extend(eval_results)
        
        # 戦略2: 日付を含む全div要素（補完用）
        div_results = self._extract_from_date_divs(soup, current_date)
        all_detected_reviews.extend(div_results)
        
        # 戦略3: 曖昧パターン検索（補完用）
        fuzzy_results = self._extract_fuzzy_patterns(soup, current_date)
        all_detected_reviews.extend(fuzzy_results)
        
        # ★修正版：厳密な重複除去（同じ日付は1件のみ）
        unique_reviews = self._strict_deduplicate_reviews(all_detected_reviews)
        
        # 30日以内フィルタリング
        final_reviews = []
        for review in unique_reviews:
            days_ago = review.get('days_ago', float('inf'))
            if 0 <= days_ago <= 30:
                final_reviews.append(review)
        
        return len(final_reviews)
    
    def _strict_deduplicate_reviews(self, all_reviews):
        """厳密な重複除去 - 同じ日付（days_ago）は1件のみ"""
        
        unique_reviews = []
        seen_days = set()  # 日付をキーとして重複チェック
        
        # メイン評価を優先するため、ソース順に処理
        # 優先順位: メイン評価・感想 > その他
        priority_reviews = []
        other_reviews = []
        
        for review in all_reviews:
            if 'メイン評価' in review.get('source', ''):
                priority_reviews.append(review)
            else:
                other_reviews.append(review)
        
        # 優先順位の高いものから処理
        for review in priority_reviews + other_reviews:
            days_ago = review.get('days_ago')
            
            # 同じ日付が既に存在する場合はスキップ
            if days_ago not in seen_days:
                seen_days.add(days_ago)
                unique_reviews.append(review)
        
        return unique_reviews
    
    def _extract_from_main_evaluation(self, soup, current_date):
        """メイン評価・感想セクションから抽出"""
        
        results = []
        
        # 評価・感想の見出しを探す
        main_headings = ['評価・感想', '評価', 'レビュー']
        
        for heading_text in main_headings:
            heading = soup.find(['h1', 'h2', 'h3', 'h4'], string=re.compile(heading_text))
            if heading:
                # 見出しの後のセクションを探す
                section = heading.find_next(['div', 'section'])
                if section:
                    dates = self._extract_dates_from_element(section, current_date, "メイン評価・感想")
                    results.extend(dates)
                break
        
        return results
    
    def _extract_from_date_divs(self, soup, current_date):
        """日付を含むdiv要素から抽出"""
        
        results = []
        
        # 日付パターンを含むdiv要素を探す
        date_patterns = [r'\d+日前', r'\d+週間前', r'\d+ヶ月前', r'\d{1,2}月\d{1,2}日']
        
        for pattern in date_patterns:
            divs = soup.find_all('div', string=re.compile(pattern))
            for div in divs:
                dates = self._extract_dates_from_element(div, current_date, f"日付div({pattern})")
                results.extend(dates)
        
        return results
    
    def _extract_fuzzy_patterns(self, soup, current_date):
        """曖昧パターンでの抽出"""
        
        results = []
        page_text = soup.get_text()
        
        # 多様な日付表現
        fuzzy_patterns = [
            (r'(\d+)\s*日前', lambda m: int(m.group(1))),
            (r'(\d+)\s*週間前', lambda m: int(m.group(1)) * 7),
            (r'(\d+)\s*ヶ月前', lambda m: int(m.group(1)) * 30),
        ]
        
        for pattern, calc_func in fuzzy_patterns:
            matches = re.finditer(pattern, page_text)
            for match in matches:
                try:
                    days_ago = calc_func(match)
                    results.append({
                        'original': match.group(0),
                        'days_ago': days_ago,
                        'type': 'fuzzy',
                        'source': '曖昧パターン'
                    })
                except:
                    pass
        
        return results
    
    def _extract_dates_from_element(self, element, current_date, source_name):
        """要素から日付を抽出"""
        
        element_text = element.get_text(strip=True)
        return self._extract_dates_from_text(element_text, current_date, source_name)
    
    def _extract_dates_from_text(self, text, current_date, source_name):
        """テキストから日付を抽出"""
        
        results = []
        
        # 相対日付パターン
        relative_patterns = [
            (r'(\d+)\s*日前', 1),
            (r'(\d+)\s*週間前', 7),  
            (r'(\d+)\s*ヶ月前', 30),
        ]
        
        for pattern, multiplier in relative_patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                try:
                    num = int(match)
                    days_ago = num * multiplier
                    
                    results.append({
                        'original': f"{num}{'日' if multiplier==1 else '週間' if multiplier==7 else 'ヶ月'}前",
                        'days_ago': days_ago,
                        'type': 'relative',
                        'source': source_name
                    })
                except:
                    pass
        
        # 絶対日付パターン
        absolute_pattern = r'(\d{1,2})月(\d{1,2})日'
        matches = re.findall(absolute_pattern, text)
        
        for month_str, day_str in matches:
            try:
                month, day = int(month_str), int(day_str)
                
                if 1 <= month <= 12 and 1 <= day <= 31:
                    year = current_date.year
                    review_date = datetime(year, month, day)
                    
                    if review_date > current_date:
                        review_date = datetime(year - 1, month, day)
                    
                    days_ago = (current_date - review_date).days
                    
                    results.append({
                        'original': f"{month}月{day}日",
                        'days_ago': days_ago,
                        'type': 'absolute',
                        'source': source_name
                    })
            except:
                pass
        
        return results
    
    def extract_service_data(self, service_url):
        """サービス詳細ページから必要なデータを抽出（修正版30日機能付き）"""
        
        try:
            response = self.session.get(service_url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            current_date = datetime.now()
            
            # データ初期化
            data = {
                'service_url': service_url,
                'service_name': '',
                'rating': 0.0,
                'description_length': 0,
                'has_faq': False,
                'has_sample_conversation': False,
                'recent_30_days_reviews': 0,
                'price': '',
                'total_reviews': 0
            }
            
            # JSON-LD構造化データから基本情報を抽出
            json_ld_scripts = soup.find_all('script', type='application/ld+json')
            for script in json_ld_scripts:
                try:
                    json_data = json.loads(script.string)
                    if json_data.get('@type') == 'Product':
                        data['service_name'] = json_data.get('name', '')
                        
                        offers = json_data.get('offers', {})
                        if offers.get('price'):
                            data['price'] = f"{offers['price']:,}円"
                        
                        aggregate_rating = json_data.get('aggregateRating', {})
                        if aggregate_rating:
                            data['rating'] = float(aggregate_rating.get('ratingValue', 0))
                            data['total_reviews'] = int(aggregate_rating.get('reviewCount', 0))
                        
                        description = json_data.get('description', '')
                        data['description_length'] = len(description)
                        break
                except (json.JSONDecodeError, ValueError, TypeError):
                    continue
            
            # HTML解析での補完
            if not data['service_name']:
                title = soup.find('h1')
                if title:
                    data['service_name'] = title.get_text(strip=True)
            
            # FAQの有無を確認
            faq_keywords = ['FAQ', 'よくある質問', 'Q&A', 'question']
            page_text = soup.get_text().lower()
            for keyword in faq_keywords:
                if keyword.lower() in page_text:
                    data['has_faq'] = True
                    break
            
            # トークルーム回答例の有無を確認
            conversation_keywords = ['トークルーム', '回答例', 'サンプル会話', 'やりとり例']
            for keyword in conversation_keywords:
                if keyword in soup.get_text():
                    data['has_sample_conversation'] = True
                    break
            
            # ★ 修正版30日レビュー数抽出（厳密な重複除去）
            data['recent_30_days_reviews'] = self.extract_30day_reviews_fixed(soup, current_date)
            
            return data
            
        except Exception as e:
            print(f"サービスページ取得エラー ({service_url}): {e}")
            return None
    
    def scrape_category_ranking(self, category_info):
        """カテゴリのランキングTOP10をスクレイピング（修正版）"""
        
        print(f"\n{'='*60}")
        print(f"カテゴリ: {category_info['category_name']}")
        print(f"URL: {category_info['url']}")
        print(f"{'='*60}")
        
        # 1. ランキング順でサービスURLを取得
        service_urls = self.get_ranking_services(category_info['url'], limit=10)
        print(f"ランキングTOP{len(service_urls)}を取得")
        
        if not service_urls:
            print("サービスURLが取得できませんでした")
            return []
        
        # 2. 各サービスの詳細データを取得
        results = []
        for i, url in enumerate(service_urls):
            print(f"\n{i+1}位: データ取得中...")
            data = self.extract_service_data(url)
            if data:
                # カテゴリ情報とランキングを追加
                data['category_name'] = category_info['category_name']
                data['category_url'] = category_info['url']
                data['ranking'] = i + 1
                results.append(data)
                print(f"  ✓ {data['service_name'][:50]}...")
                print(f"    価格: {data['price']}, 評価: {data['rating']} ({data['total_reviews']}件)")
                print(f"    ★30日レビュー: {data['recent_30_days_reviews']}件 (修正版)")
            else:
                print(f"  ✗ データ取得失敗: {url}")
            
            # レート制限
            time.sleep(self.delay)
        
        return results
    
    def scrape_multiple_categories(self, categories):
        """複数カテゴリのランキングをスクレイピング"""
        
        all_results = []
        
        for i, category in enumerate(categories):
            print(f"\n{'='*80}")
            print(f"進行状況: {i+1}/{len(categories)} カテゴリ")
            print(f"{'='*80}")
            
            results = self.scrape_category_ranking(category)
            all_results.extend(results)
            
            # カテゴリ間で休憩
            if i < len(categories) - 1:
                print(f"\n次のカテゴリまで{self.delay * 2}秒待機...")
                time.sleep(self.delay * 2)
        
        return all_results

def main():
    """メイン処理"""
    
    parser = argparse.ArgumentParser(description='ココナラ カテゴリランキングTOP10スクレイピングツール（修正版）')
    parser.add_argument('--categories', type=int, default=1, help='処理するカテゴリ数 (デフォルト: 1)')
    parser.add_argument('--delay', type=float, default=2.0, help='リクエスト間隔（秒） (デフォルト: 2.0)')
    parser.add_argument('--output', type=str, default='coconala_ranking_fixed.csv', help='出力ファイル名')
    
    args = parser.parse_args()
    
    # CSVからカテゴリ情報を読み込み
    try:
        df = pd.read_csv('/Users/my/Desktop/coding/coco-research03/list/category_sheet_v1_20250630 - シート1.csv')
        # メインカテゴリのみ選択（Category_level=1）
        main_categories = df[df['Category_level'] == 1]
        
        # カテゴリ情報を変換
        categories = []
        for _, row in main_categories.head(args.categories).iterrows():
            category_info = {
                'category_name': row['第一階層'],
                'url': f"https://coconala.com/categories/{row['カテゴリ番号']}",
                'main_category_id': row['カテゴリ番号'],
                'category_level': row['Category_level']
            }
            categories.append(category_info)
    except FileNotFoundError:
        print("エラー: list/category_sheet_v1_20250630 - シート1.csv ファイルが見つかりません")
        return
    
    # スクレイピング実行
    scraper = CoconalaScraperFixed(delay=args.delay)
    results = scraper.scrape_multiple_categories(categories)
    
    if results:
        # 結果をCSVで保存
        results_df = pd.DataFrame(results)
        
        # 列の順序を整理（ランキング順を最初に）
        columns_order = [
            'ranking', 'category_name', 'service_name', 'rating', 
            'description_length', 'has_faq', 'has_sample_conversation', 
            'recent_30_days_reviews', 'price', 'total_reviews', 
            'service_url', 'category_url'
        ]
        results_df = results_df[columns_order]
        
        # ファイル名にタイムスタンプを追加
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = f'/Users/my/Desktop/coding/coco-research03/output/{timestamp}_{args.output}'
        results_df.to_csv(output_file, index=False, encoding='utf-8')
        
        print(f"\n{'='*80}")
        print("スクレイピング完了！（修正版）")
        print(f"処理したカテゴリ数: {len(categories)}")
        print(f"取得したサービス総数: {len(results)}")
        print(f"結果ファイル: {output_file}")
        
        # 結果サマリーを表示
        print(f"\n=== 結果サマリー（修正版） ===")
        print(f"平均評価点: {results_df['rating'].mean():.2f}")
        print(f"平均説明文文字数: {results_df['description_length'].mean():.0f}")
        print(f"FAQ有りサービス数: {results_df['has_faq'].sum()}")
        print(f"トークルーム回答例有りサービス数: {results_df['has_sample_conversation'].sum()}")
        print(f"平均総レビュー数: {results_df['total_reviews'].mean():.1f}")
        print(f"★平均30日レビュー数（修正版）: {results_df['recent_30_days_reviews'].mean():.1f}")
        
    else:
        print("データ取得に失敗しました")

if __name__ == "__main__":
    main()
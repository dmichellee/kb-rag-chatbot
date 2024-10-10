import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import os
import json

def crawl_page(url, base_url, visited=set(), output_dir='crawled_data'):
    if url in visited:
        return

    visited.add(url)
    print(f"Crawling: {url}")

    # 출력 디렉토리 생성
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')

        # URL에서 파일 이름 생성
        file_name = urlparse(url).path.strip('/').replace('/', '_') or 'index'

        # 텍스트 추출 및 저장
        text = soup.get_text()
        with open(os.path.join(output_dir, f"{file_name}_text.txt"), 'w', encoding='utf-8') as f:
            f.write(text)

        # PDF 및 기타 첨부 파일 추출 및 저장
        attachments = soup.find_all('a', href=lambda href: href and href.endswith(('.pdf', '.doc', '.docx', '.xls', '.xlsx')))
        attachment_dir = os.path.join(output_dir, f"{file_name}_attachments")
        if not os.path.exists(attachment_dir):
            os.makedirs(attachment_dir)

        for attachment in attachments:
            attachment_url = urljoin(base_url, attachment['href'])
            try:
                attachment_response = requests.get(attachment_url)
                if attachment_response.status_code == 200:
                    attachment_filename = os.path.basename(urlparse(attachment_url).path)
                    attachment_path = os.path.join(attachment_dir, attachment_filename)
                    
                    with open(attachment_path, 'wb') as attachment_file:
                        attachment_file.write(attachment_response.content)
                    print(f"Saved attachment: {attachment_path}")
            except Exception as e:
                print(f"Error saving attachment {attachment_url}: {e}")

        # 링크 추출 및 저장
        links = soup.find_all('a')
        link_data = []
        for link in links:
            href = link.get('href')
            if href:
                full_url = urljoin(base_url, href)
                link_data.append({
                    'text': link.text.strip(),
                    'url': full_url
                })
                # 같은 도메인 내의 링크만 크롤링
                if urlparse(full_url).netloc == urlparse(base_url).netloc:
                    crawl_page(full_url, base_url, visited, output_dir)

        with open(os.path.join(output_dir, f"{file_name}_links.json"), 'w', encoding='utf-8') as f:
            json.dump(link_data, f, ensure_ascii=False, indent=2)

        print(f"Saved data for: {url}")

    except Exception as e:
        print(f"Error crawling {url}: {e}")

# 크롤링 시작
base_url = 'https://aws.amazon.com/ko/events/industry-week/'
crawl_page(base_url, base_url)
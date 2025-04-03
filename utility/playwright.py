from playwright.async_api import async_playwright
import os
import json
# LeetCode authentication tokens
LEETCODE_CSRFTOKEN = os.getenv("LEETCODE_CSRFTOKEN")
LEETCODE_SESSION = os.getenv("LEETCODE_SESSION")
LEETCODE_CF_CLEARANCE = os.getenv("LEETCODE_CF_CLEARANCE")
async def fetch_leetcode_page_with_playwright(url):
    """Use Playwright to fetch a LeetCode page with browser cookies"""
    try:
        async with async_playwright() as p:
            # Launch the browser with options to avoid detection
            browser = await p.chromium.launch(
                headless=True,
                args=[
                    '--disable-blink-features=AutomationControlled',
                    '--no-sandbox',
                    '--disable-web-security',
                    '--disable-features=IsolateOrigins,site-per-process'
                ]
            )
            
            # Create a context with viewport and device scale factor
            context = await browser.new_context(
                viewport={'width': 1280, 'height': 800},
                device_scale_factor=2,
                user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36'
            )
            
            # Set cookies for authentication using environment variables
            cookies = [
                {
                    "name": "csrftoken",
                    "value": LEETCODE_CSRFTOKEN,
                    "domain": ".leetcode.com",
                    "path": "/"
                },
                {
                    "name": "LEETCODE_SESSION",
                    "value": LEETCODE_SESSION,
                    "domain": ".leetcode.com",
                    "path": "/"
                },
                {
                    "name": "cf_clearance",
                    "value": LEETCODE_CF_CLEARANCE,
                    "domain": ".leetcode.com",
                    "path": "/"
                },
                # Additional cookies from .env
                {
                    "name": "87b5a3c3f1a55520_gr_cs1",
                    "value": os.getenv("87b5a3c3f1a55520_gr_cs1"),
                    "domain": ".leetcode.com",
                    "path": "/"
                },
                {
                    "name": "87b5a3c3f1a55520_gr_last_sent_cs1",
                    "value": os.getenv("87b5a3c3f1a55520_gr_last_sent_cs1"),
                    "domain": ".leetcode.com",
                    "path": "/"
                },
                {
                    "name": "INGRESSCOOKIE",
                    "value": os.getenv("INGRESSCOOKIE"),
                    "domain": ".leetcode.com",
                    "path": "/"
                },
                {
                    "name": "__stripe_mid",
                    "value": os.getenv("__stripe_mid"),
                    "domain": ".leetcode.com",
                    "path": "/"
                },
                {
                    "name": "_ga",
                    "value": os.getenv("_ga"),
                    "domain": ".leetcode.com",
                    "path": "/"
                },
                {
                    "name": "gr_user_id",
                    "value": os.getenv("gr_user_id"),
                    "domain": ".leetcode.com",
                    "path": "/"
                },
                {
                    "name": "ip_check",
                    "value": os.getenv("ip_check"),
                    "domain": ".leetcode.com",
                    "path": "/"
                }
            ]
            
            await context.add_cookies(cookies)
            
            # Create a new page and navigate to the URL
            page = await context.new_page()
            
            # Set headers to mimic a real browser
            await page.set_extra_http_headers({
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                'Accept-Language': 'en-US,en;q=0.9',
                'Cache-Control': 'no-cache',
                'Pragma': 'no-cache',
                'Sec-Ch-Ua': '"Google Chrome";v="123", "Not:A-Brand";v="8", "Chromium";v="123"',
                'Sec-Ch-Ua-Mobile': '?0',
                'Sec-Ch-Ua-Platform': '"macOS"',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none',
                'Sec-Fetch-User': '?1',
                'Upgrade-Insecure-Requests': '1'
            })
            
            # Enable request/response logging
            page.on("request", lambda request: print(f">> Request: {request.method} {request.url}"))
            page.on("response", lambda response: print(f"<< Response: {response.status} {response.url}"))
            
            # Navigate to the URL with a longer timeout
            print(f"Navigating to {url}")
            response = await page.goto(url, wait_until="networkidle", timeout=60000)
            status_code = response.status
            headers = response.headers
            
            # Print response details
            print(f"Response status code: {status_code}")
            print(f"Response headers: {json.dumps(headers, indent=2)}")
            
            # Wait for the page to fully load
            await page.wait_for_load_state("networkidle")
            
            # Get the page content
            html_content = await page.content()
            
            # Print content sample
            content_sample = html_content[:200] + "..." if html_content and len(html_content) > 200 else html_content
            print(f"Content sample: {content_sample}")
            print(f"Content length: {len(html_content) if html_content else 0}")
            
            # Close the browser
            await browser.close()
            
            return html_content, status_code
    except Exception as e:
        print(f"Playwright error: {str(e)}")
        import traceback
        print(traceback.format_exc())
        return None, 500

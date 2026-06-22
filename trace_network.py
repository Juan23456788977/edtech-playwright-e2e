import time
from playwright.sync_api import sync_playwright

def run():
    p = sync_playwright().start()
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={'width': 1366, 'height': 900})
    
    def handle_request(request):
        print(f">>> {request.method} {request.url}")
    
    def handle_response(response):
        if response.status >= 300 and response.status < 400:
            print(f"<<< {response.status} {response.url} -> {response.headers.get('location')}")
        else:
            print(f"<<< {response.status} {response.url}")
            
    page.on("request", handle_request)
    page.on("response", handle_response)
    
    page.goto('https://alpha.akdemia.com/login')
    page.fill('#email_login', 'jcortez@akdemia.com')
    page.fill('#password_login', 'akdemia#2026*')
    page.click('input[type="submit"]')
    page.wait_for_load_state('networkidle')
    time.sleep(2)

    page.evaluate('''
    document.getElementById('selected-instance-type').value = 'Employee';
    document.getElementById('selected-instance-id').value = '17548';
    document.getElementById('select-role-form').submit();
    ''')
    time.sleep(5)

    print("================== READY TO CLICK ==================")
    email = 'rossiz2303@gmail.com'
    page.evaluate('''() => {
        var modal = document.getElementById('change-to-any-user-modal');
        if(modal) {
            modal.classList.add('show', 'in');
            modal.style.display = 'block';
            document.body.classList.add('modal-open');
        }
    }''')
    time.sleep(1)

    page.fill('#fill-user-info', email)
    page.press('#fill-user-info', 'Enter')
    time.sleep(4)

    page.evaluate('''() => {
        var a = document.querySelector('#search-results a');
        if(a) a.click();
    }''')
    
    time.sleep(10)
    page.close()
    browser.close()
    p.stop()

if __name__ == '__main__':
    run()

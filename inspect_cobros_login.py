from playwright.sync_api import sync_playwright

def run():
    p = sync_playwright().start()
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    try:
        page.goto("https://cobros.akdemia.com/")
        page.wait_for_load_state("networkidle")
        print("URL:", page.url)
        # Find all inputs
        inputs = page.locator("input")
        count = inputs.count()
        print(f"Total inputs: {count}")
        for i in range(count):
            inp = inputs.nth(i)
            print(f"Input {i}: type={inp.get_attribute('type')}, id={inp.get_attribute('id')}, name={inp.get_attribute('name')}, placeholder={inp.get_attribute('placeholder')}")
    except Exception as e:
        print("Error:", e)
    finally:
        browser.close()
        p.stop()

if __name__ == "__main__":
    run()

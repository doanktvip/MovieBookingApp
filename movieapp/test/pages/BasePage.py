class BasePage:
    def __init__(self, driver):
        self.driver = driver

    def open(self, url):
        self.driver.get(url)

    def find(self, by, value):
        return self.driver.find_element(by, value)

    def finds(self, by, value):
        return self.driver.find_elements(by, value)

    def click(self, by, value):
        self.find(by, value).click()

    def js_click(self, by, value):
        element = self.find(by, value)
        self.driver.execute_script("arguments[0].click();", element)

    def js_clicks(self, by, value):
        elements = self.finds(by, value)
        self.driver.execute_script("arguments[0].click();", elements[0])

    def typing(self, by, value, text):
        e = self.find(by, value)
        e.send_keys(text)

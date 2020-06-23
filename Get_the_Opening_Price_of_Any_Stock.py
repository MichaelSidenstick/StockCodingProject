from selenium import webdriver
from selenium.webdriver.chrome.options import Options

# Get Ticker and Make URL
ticker = input("Stock ticker (All Caps): ")
url = "https://finance.yahoo.com/quote/" + ticker + "?p=" + ticker

# Path to Chrome Driver
DRIVER_PATH = r'C:\Brians Stuff\Coding\Python\chromedriver_win32\chromedriver'
# Open browser/server connection
options = Options()
options.headless = True
options.add_argument("--window-size=1920,1200")
driver = webdriver.Chrome(options=options, executable_path=DRIVER_PATH)
# Go to yahoo finance
#driver.get("https://finance.yahoo.com/quote/AAPL?p=AAPL")
driver.get(url)
# Get the opening price
h1 = driver.find_element_by_xpath("""//*[@id="quote-summary"]/div[1]/table/tbody/tr[2]/td[2]/span""")
open_price = float(h1.text)
driver.quit()

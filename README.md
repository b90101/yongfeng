# 箱型理論驗證專案

這是一個可以套用箱型理論驗證是否賺錢的小專案。

## 安裝依賴

首先，執行以下指令安裝所需的 Python 套件：

```bash
pip install -r requirements.txt
```

## 使用前準備

使用本專案前，需要申請永豐證券帳戶並啟用 API 服務。

### 申請步驟

1. 申請永豐證券帳戶。
2. 前往 [永豐證券簽署中心](https://www.sinotrade.com.tw/) 簽署 API 文件。
3. 申請通過後，前往 [永豐證券 API 管理頁面](https://www.sinotrade.com.tw/) 申請 API Key。
4. 申請完成後，需要在測試環境進行模擬下單。

## 程式碼範例

以下是測試環境下單的 Python 程式碼範例：

```python
import os
from dotenv import load_dotenv
import shioaji as sj
from shioaji.constant import Action, StockPriceType, OrderType

def testing_stock_ordering():
    # 測試環境登入
    load_dotenv()
    api = sj.Shioaji(simulation=True)  # simulation=True 為測試環境
    api.login(
        api_key=os.environ["API_KEY"],
        secret_key=os.environ["SECRET_KEY"]
    )

    api.activate_ca(
        ca_path="憑證地址",
        ca_passwd="預設身分證",
    )

    # 準備下單的 Contract
    # 使用 2890 永豐金為例
    contract = api.Contracts.Stocks["2890"]
    print(f"Contract: {contract}")

    # 建立委託下單的 Order
    order = sj.order.StockOrder(
        action=Action.Buy,  # 買進
        price=contract.reference,  # 以平盤價買進
        quantity=1,  # 下單數量
        price_type=StockPriceType.LMT,  # 限價單
        order_type=OrderType.ROD,  # 當日有效單
        account=api.stock_account,  # 使用預設的帳戶
    )
    print(f"Order: {order}")

    # 送出委託單
    trade = api.place_order(contract=contract, order=order)
    print(f"Trade: {trade}")

    # 更新狀態
    api.update_status()
    print(f"Status: {trade.status}")

testing_stock_ordering()
```

## 登入相關影片

### 相關網站

- [Shioaji 官方網站](https://www.sinotrade.com.tw/)
- [SinoTrade 主頁](https://www.sinotrade.com.tw/)
- [Shioaji YouTube 影片教學](https://www.youtube.com/)
- [永豐證券](https://www.sinotrade.com.tw/)

## 執行交易

模擬下單後，即可使用 `main.py` 執行。

```python
if __name__ == "__main__":
    stock_id = "輸入你的代號"
    start_date = "輸入你的開始日期"

```

請替換 `stock_id` 為股票代號，`start_date` 為預計開始日期，
設定完成後，執行程式即可開始交易。

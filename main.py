import os
from dotenv import load_dotenv
import shioaji as sj
import pandas as pd
import mplfinance as mpf
from datetime import datetime, timedelta

load_dotenv()

HOLIDAYS = {
    "2024-01-01",  # 元旦
    "2024-02-09",  # 春節除夕
    "2024-02-10",  # 春節初一
    "2024-02-11",  # 春節初二
    "2024-02-12",  # 春節初三（補假）
    "2024-02-13",  # 春節假期（補假）
    "2024-02-28",  # 和平紀念日
    "2024-04-04",  # 兒童節
    "2024-04-05",  # 清明節
    "2024-06-10",  # 端午節
    "2024-09-17",  # 中秋節
    "2024-10-10",  # 國慶日
    "2025-01-01"   # 元旦
}

#日期
def add_business_days(start_date: str, days_to_add: int) -> str:
    # 將日期字串轉為 datetime 物件
    date = datetime.strptime(start_date, "%Y-%m-%d")
    added_days = 0

    while added_days < days_to_add:
        # 日期加一天
        date += timedelta(days=1)
        
        # 檢查是否是週末或國定假日
        if date.weekday() >= 5:  # 週六 (5) 或週日 (6)
            continue
        if date.strftime("%Y-%m-%d") in HOLIDAYS:  # 國定假日
            continue
        
        # 若為工作日，計數器加一
        added_days += 1

    # 返回計算後的日期
    return date.strftime("%Y-%m-%d")


#算 支撐位 壓力位
def calculate_box(df): 
    # 計算支撐位與壓力位
    support = df['Low'].min()   # 最低點作為支撐位
    resistance = df['High'].max()  # 最高點作為壓力位
    return support, resistance


#繪製 k 線圖
def plot_kline_with_box(df, stock_name,support, resistance): 
    # 計算支撐位與壓力位

    mc = mpf.make_marketcolors(up='r', down='g', inherit=True)
    s = mpf.make_mpf_style(base_mpf_style='yahoo', marketcolors=mc)

    # 設定繪圖參數
    kwargs = dict(
        type='candle',          # 繪製 K 線圖
        mav=(5, 20, 60),        # 移動平均線
        volume=True,            # 顯示成交量
        figratio=(16, 9),       # 寬高比，讓圖形更寬
        figscale=1.2,           # 圖形比例，讓圖形更大
        title=stock_name,       # 標題
        style=s,                # 自訂樣式
        tight_layout=True,      # 自動調整布局，避免擠在一起
        datetime_format='%Y-%m-%d',  # X 軸顯示格式
        xrotation=20            # X 軸刻度旋轉，避免重疊
    )

    add_lines = [
        mpf.make_addplot([support] * len(df), color='green', linestyle='--', width=1, label='Support'),
        mpf.make_addplot([resistance] * len(df), color='red', linestyle='--', width=1, label='Resistance')
    ]

    mpf.plot(df, addplot=add_lines, **kwargs)


def fetch_kline(id): #獲取一年 k 線
    api = sj.Shioaji(simulation=False)
    api.login(
        api_key=os.environ["API_KEY"],
        secret_key=os.environ["SECRET_KEY"]
    )

    api.activate_ca(
        ca_path= "./Sinopac.pfx",
        ca_passwd= os.environ["ca_passwd"],
    )

    contract = api.Contracts.Stocks[id]

    kline_data = api.kbars(
        contract=contract,
        start="2024-01-01",
        end="2025-01-01"
    )

    df = pd.DataFrame({**kline_data})
    df.ts = pd.to_datetime(df.ts)  
    df.set_index('ts', inplace=True)  

    daily_df = df.resample('D').agg({
        'Open': 'first',
        'High': 'max',
        'Low': 'min',
        'Close': 'last',
        'Volume': 'sum',
        'Amount': 'sum'
    }).dropna()  

    daily_df.drop(columns=['Amount'], inplace=True)

    return daily_df

def simulated_trading(df, purchase_date):
    # 設定成本價（假設已經取得）
    if purchase_date in df.index:
        purchase_price = df.loc[purchase_date, 'Open']
        print(f"成本價：{purchase_price}")
    else:
        print(f"無法取得 {purchase_date} 的資料")
        return None  # 如果找不到購買日期的資料，結束模擬

    current_date = add_business_days(purchase_date, 1)  # 開始檢查的下一個交易日

    while current_date!= "2025-01-01":
        if current_date in df.index :
        # 取得當天的收盤價（可改成其他指標如開盤價）
            close_price = df.loc[current_date, 'Close']

            if resistance * 1.05 <= close_price <= resistance * 1.10:
                profit = close_price - purchase_price
                total_profit = profit * 1000  # 一張股票的總收益
                print(f"突破範圍，賣出價：{close_price}, 獲利：{total_profit}")
                return current_date,total_profit

            elif close_price < resistance :
                loss = purchase_price - close_price
                total_loss = loss * 1000  # 一張股票的總損失
                print(f"跌回範圍，賣出價：{close_price}, 損失：{total_loss}")
                return current_date,-total_loss

            # 若未觸發條件，繼續檢查下一天
            print("未觸發條件，繼續檢查下一天")
            current_date = add_business_days(current_date, 1)
        else:
            current_date = add_business_days(current_date, 1)

    print("價格未觸及任何條件，模擬結束")
    return 0  # 未觸發條件時，回傳 0 表示無交易結果




if __name__ == "__main__":
    stock_id = "輸入你的代號"
    df = fetch_kline(stock_id)
    box_len = 30
    start_date = "輸入你的開始日期"
    

    while start_date != "2025-01-01":
        end_date = add_business_days(start_date, box_len-1)
        print(f"開始日期:{start_date} , 日期:{end_date}")

        #抓取箱體 算出壓力位 and 支撐位
        filtered_df = df.loc[start_date:end_date] #抓取箱體大小數據
        last_date_data =  filtered_df.iloc[-1] #抓取最後一日 查看是否突破箱體
        support, resistance = calculate_box(filtered_df) #計算壓力位 支撐位

        #如果突破(>=) 那就進入我們的購買策略
        if last_date_data.Close >= resistance:
            dd = last_date_data.name #獲取最後一天日期

            print(f"找到突破箱體訊號 日期:{dd.date()}")
            print(f"支撐位: {support}, 壓力位: {resistance}")
    
            purchase_date = add_business_days(str(dd.date()), 1) #購買日為突破箱體隔天
            current_date,total_profit = simulated_trading(df,purchase_date) #獲取最後交易日 還有損益
            output_df = df.loc[start_date:current_date]  #獲取箱體到最後交易日 所有數據 方便繪製是賺還是賠錢
            plot_kline_with_box(output_df, stock_id,support, resistance) #繪製圖形
            break
        else:
            print("未找到突破箱體訊號")
            start_date  = add_business_days(start_date, 1)
            #未找到 則往下一天前進 繼續尋找有望突破壓力位的訊號

    
    

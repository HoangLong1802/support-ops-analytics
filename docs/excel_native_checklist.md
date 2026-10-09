# Kiểm tra Excel native

Ngày 08/10/2026 xác nhận EXCEL.EXE tồn tại tại C:\Program Files\Microsoft Office\root\Office16\EXCEL.EXE. Computer Use thất bại ngay khi sky.list_apps với native pipe unavailable / file not found (os error 2), trước bước mở workbook hoặc chọn cửa sổ. Kiểm tra Codex Document Control cũng không có connected document session để điều khiển qua add-in. Vì vậy chưa kiểm tra formula bar, chart rendering, filter interactions, hiển thị hoặc capture native. CScript Access denied thuộc lần thử trước, không phải kết quả native mở mới trong phiên này.

Workbook output/customer_support_analysis.xlsx có 14 sheets và 5 Excel chart objects. Đây là summary export tĩnh, không có formulas/PivotTables. Parser kiểm tra metadata/filter/chart objects không thay thế việc mở Excel. Ảnh images/workbook vẫn gọi workbook render từ Artifact Tool; không có screenshot Excel thật.

Các bước cần làm trên Excel tương tác:

1. File → Open → output/customer_support_analysis.xlsx; ghi phiên bản Excel và mọi thông báo repair/error. Không ghi native PASS nếu mở có repair.
2. README: kiểm tra 8 KPI overview, SLA chart và text không bị cắt. Executive_KPIs: 42 rows, chọn vài value cells và xem formula bar: số tĩnh, không công thức bắt đầu bằng =.
3. Demand_Analysis: chart monthly có 12 labels Oct 25…Sep 26, không serial dates; filter một month trong table, kiểm tra menu hoạt động rồi Clear filter. Xác nhận Freeze Panes khi scroll.
4. SLA_Analysis: check outcomes/rates/eligible N; chart hiển thị đúng MET/BREACHED/PENDING. Backlog_Analysis: aging chart 6 bins, tổng 578; labels không chồng nhau.
5. Team_Performance: chart thứ 5 và table/format; Cleaning_Summary/Data_Quality: cột dài, row height, headings không cắt; kiểm tra các sheets còn lại bằng zoom và scroll.
6. So Executive_KPIs với verified_kpis.csv: total 14.774; resolution compliance 76,187572%; backlog 578; CSAT 4,0714574082. Rates hiển thị rounding, underlying values giữ precision.
7. Không cần tạo công thức để “recalculate” summary này. Nếu File → Info có external links hoặc warning bất thường, ghi lại và kiểm tra trước khi save. Các chart series dùng cells trong workbook.
8. Capture cửa sổ Excel thật bằng screenshot, lưu images/excel_native/overview.png và demand.png; ghi sheet, range/zoom, phiên bản, ngày capture. Chỉ dùng nhãn screenshot Excel khi nguồn là capture này. Không đổi nhãn hai workbook renders hiện có.

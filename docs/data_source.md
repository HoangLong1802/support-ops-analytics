# Nguồn và quyền sử dụng dữ liệu

Cả 5 raw CSV là dữ liệu mô phỏng được tạo bằng [generator trong repo](../tools/synthetic_data_generator.py), seed 42. Không lấy từ ticket doanh nghiệp, Kaggle hoặc API vận hành. Agent IDs là mã giả; không có tên khách hàng, email, số điện thoại hoặc nội dung hội thoại.

[Metadata](../data/analytics/generation_metadata.json) ghi parameters, calibration history và SHA256. Raw đã frozen; không chạy generator để resume. Simulation chủ động tạo distributions, associations và defects để thực hành. Technical/weekday patterns là đặc tính simulation, không phải phát hiện độc lập từ dữ liệu doanh nghiệp.

Coverage tạo ticket là 01/10/2025 đến hết 30/09/2026 theo Asia/Ho_Chi_Minh; 365 ngày. Timestamp nguồn có UTC Z. Snapshot backlog là 01/10/2026 00:00 local, tương đương 30/09/2026 17:00 UTC. Coverage từ contract cho phép giữ zero-ticket days trong mẫu số.

Không có nguồn CSV bên thứ ba cần xin quyền phân phối trong dataset này. Repo chưa có LICENSE cấp quyền tái sử dụng chung; public visibility không tự cấp license. Tác giả cần chọn LICENSE trước khi cấp quyền phân phối lại code/data. Nhiệm vụ này chỉ sửa local, không push, publish hoặc đổi quyền truy cập.

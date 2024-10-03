from flask import Flask, request, render_template, redirect, url_for
from api.getOrderList import get_order_list
from api.getContactList import get_contact_list
from baseopensdk import BaseClient 
from function.order_process import process_order
from function.customer_process import process_customer

# Chỉ định thư mục chứa template là 'view'
app = Flask(__name__, template_folder='view')

@app.route('/', methods=['GET', 'POST'])
def choose_type():
    if request.method == 'POST':
        # Lấy lựa chọn từ form
        api_type = request.form['api_type']
        # Chuyển hướng đến trang tương ứng dựa trên lựa chọn
        if api_type == 'get_order':
            return redirect(url_for('order_form'))
        elif api_type == 'get_customer':
            return redirect(url_for('contact_form'))
    # Render trang chọn loại sync
    return render_template('choose_type.html')

@app.route('/contact_form', methods=['GET', 'POST'])
def contact_form():
    if request.method == 'POST':
        # Lấy dữ liệu từ form
        APP_TOKEN = request.form['APP_TOKEN']
        PERSONAL_BASE_TOKEN = request.form['PERSONAL_BASE_TOKEN']
        TABLE_ID = request.form['TABLE_ID']
        HARAVAN_TOKEN = request.form['HARAVAN_TOKEN']

        # Lấy các tham số bổ sung từ form
        created_at_min = request.form.get('created_at_min')
        created_at_max = request.form.get('created_at_max')
        limit = request.form.get('limit')

        # Gọi API Haravan để lấy danh sách khách hàng
        customer_data = get_contact_list(
            haravan_token=HARAVAN_TOKEN,
            created_at_min=created_at_min,
            created_at_max=created_at_max,
            limit=limit
        )

        if customer_data:
            # Gửi dữ liệu vào Base
            client = BaseClient.builder().app_token(APP_TOKEN).personal_base_token(PERSONAL_BASE_TOKEN).build()
            process_customer(client, TABLE_ID, customer_data)
            return "Customer data successfully synced to Base."
        else:
            print("Failed to sync customers.")
            return "Failed to sync customers."

    return render_template('contact_form.html')

@app.route('/order_form', methods=['GET', 'POST'])
def order_form():
    if request.method == 'POST':
        # Lấy dữ liệu từ form
        APP_TOKEN = request.form['APP_TOKEN']
        PERSONAL_BASE_TOKEN = request.form['PERSONAL_BASE_TOKEN']
        TABLE_ID = request.form['TABLE_ID']
        HARAVAN_TOKEN = request.form['HARAVAN_TOKEN']

        # Lấy các tham số bổ sung từ form
        status = request.form.get('status')
        created_at_min = request.form.get('created_at_min')
        created_at_max = request.form.get('created_at_max')
        limit = request.form.get('limit')
        page = request.form.get('page')
        order = request.form.get('order')

        # Gọi API Haravan để lấy danh sách đơn hàng
        order_data = get_order_list(
            haravan_token=HARAVAN_TOKEN,
            status=status,
            created_at_min=created_at_min,
            created_at_max=created_at_max,
            limit=limit,
            page=page,
            order=order
        )

        if order_data:
            # Gửi dữ liệu vào Base
            client = BaseClient.builder().app_token(APP_TOKEN).personal_base_token(PERSONAL_BASE_TOKEN).build()
            process_order(client, TABLE_ID, order_data)
            return "Order data successfully synced to Base."
        else:
            print("Failed to sync orders.")
            return "Failed to sync orders."

    return render_template('order_form.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=81)

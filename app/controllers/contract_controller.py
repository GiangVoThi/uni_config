from flask import Blueprint, render_template, request, send_file, jsonify
from app.services.contract_service import get_service_details, generate_contract_word, preview_contract, upsert_contract, delete_contract, get_sharepoint_data
from app.models.contract_model import dichVu, hopDong, hop_dong_dich_vu
from app.models.database import db
from sqlalchemy import text
from app.services.contract_service import (
    get_available_services as contract_service_get_services,
    list_contracts as contract_service_get_contracts,
    get_contract_details as contract_service_get_contract_by_id
)
from datetime import datetime

contract_bp = Blueprint('contract', __name__, url_prefix='/contract')

@contract_bp.route('/')
def index():
    return render_template('contract.html')

@contract_bp.route('/preview', methods=['POST'])
def preview():
    service_ids = request.form.getlist('service_ids[]')
    contract_number = request.form.get('contract_number')
    sign_date = request.form.get('sign_date')
    
    # Lấy thông tin công ty từ form
    company_info = {
        'company': request.form.get('company_name'),
        'tax_code': request.form.get('tax_code'),  # Đảm bảo lấy mã số thuế
        'address': request.form.get('company_address'),
        'representative': request.form.get('representative'),
        'position': request.form.get('position')
    }
    
    # Debug log
    print("Debug - Company Info:", company_info)
    
    if not service_ids:
        return jsonify({"error": "Vui lòng chọn ít nhất một dịch vụ!"}), 400
    if not contract_number:
        return jsonify({"error": "Vui lòng nhập số hợp đồng!"}), 400
    if not sign_date:
        return jsonify({"error": "Vui lòng chọn ngày ký!"}), 400
        
    service_details = get_service_details([int(id) for id in service_ids])
    preview_data = preview_contract(service_details, contract_number, sign_date, company_info)
    
    # Debug log
    print("Debug - Preview Data:", preview_data)
    
    return jsonify(preview_data)

@contract_bp.route('/generate_contract', methods=['POST'])
def generate_contract():
    service_ids = request.form.getlist('service_ids[]')
    contract_number = request.form.get('contract_number')
    sign_date = request.form.get('sign_date')
    
    # Lấy thông tin công ty từ form
    company_info = {
        'company': request.form.get('company_name'),
        'tax_code': request.form.get('tax_code'),
        'address': request.form.get('company_address'),
        'representative': request.form.get('representative'),
        'position': request.form.get('position')
    }
    
    if not service_ids:
        return "Vui lòng chọn ít nhất một dịch vụ!", 400
    if not contract_number:
        return "Vui lòng nhập số hợp đồng!", 400
    if not sign_date:
        return "Vui lòng chọn ngày ký!", 400
        
    service_details = get_service_details([int(id) for id in service_ids])
    file_path = generate_contract_word(service_details, contract_number, sign_date, company_info)
    return send_file(file_path, as_attachment=True)

@contract_bp.route('/api/services', methods=['GET'])
def get_services():
    """
    Lấy danh sách dịch vụ
    """
    try:
        contract_id = request.args.get('contract_id')
        
        if contract_id:
            # Nếu có contract_id, lấy các dịch vụ đã chọn cho hợp đồng đó
            query = text("""
                SELECT d.id_dich_vu, d.ten_dich_vu
                FROM dich_vu d
                JOIN hop_dong_dich_vu hdv ON d.id_dich_vu = hdv.id_dich_vu
                WHERE hdv.id_hop_dong = :contract_id
            """)
            services = db.session.execute(query, {'contract_id': contract_id})
        else:
            # Nếu không có contract_id, lấy tất cả dịch vụ
            services = db.session.query(dichVu).all()
            
        return jsonify([
            {'id': service.id_dich_vu, 'name': service.ten_dich_vu}
            for service in services
        ])
    except Exception as e:
        print(f"Error in get_services API: {str(e)}")
        return jsonify({'error': str(e)}), 500

@contract_bp.route('/api/contract', methods=['POST'])
def create_update_contract():
    """
    Tạo mới hoặc cập nhật hợp đồng
    """
    try:
        data = request.get_json()
        id_hop_dong = data.get('id_hop_dong')
        ten_hop_dong = data.get('ten_hop_dong')
        so_hop_dong = data.get('so_hop_dong')
        ngay_ky = data.get('ngay_ky')
        dich_vu_ids = data.get('dich_vu_ids', [])

        # Chuyển đổi dich_vu_ids thành list nếu không phải
        if isinstance(dich_vu_ids, str):
            try:
                # Nếu là JSON string
                import json
                dich_vu_ids = json.loads(dich_vu_ids)
            except json.JSONDecodeError:
                # Nếu là single ID
                dich_vu_ids = [int(dich_vu_ids)] if dich_vu_ids else []
        
        # Đảm bảo dich_vu_ids là list
        if not isinstance(dich_vu_ids, list):
            dich_vu_ids = list(dich_vu_ids)

        # Chuyển đổi ngày từ dd/mm/yyyy sang date object
        try:
            ngay_ky = datetime.strptime(ngay_ky, '%d/%m/%Y').date()
        except ValueError:
            return jsonify({'error': 'Định dạng ngày không hợp lệ (dd/mm/yyyy)'}), 400

        # Tạo/cập nhật hợp đồng
        result = upsert_contract(id_hop_dong, ten_hop_dong, so_hop_dong, ngay_ky, dich_vu_ids)
        
        if 'error' in result:
            return jsonify(result), 400
            
        return jsonify(result)
        
    except ValueError as e:
        return jsonify({'error': f'Dữ liệu không hợp lệ: {str(e)}'}), 400
    except Exception as e:
        print(f"Error in create_update_contract: {str(e)}")
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@contract_bp.route('/api/contract/<int:id_hop_dong>', methods=['DELETE'])
def remove_contract(id_hop_dong):
    """
    Endpoint để xóa hợp đồng
    """
    try:
        result = delete_contract(id_hop_dong)
        if 'error' in result:
            return jsonify(result), 404
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@contract_bp.route('/api/contracts', methods=['GET'])
def get_contracts():
    """
    Lấy danh sách hợp đồng từ database
    """
    try:
        contracts = contract_service_get_contracts()
        return jsonify(contracts)
    except Exception as e:
        print(f"Error in get_contracts API: {str(e)}")
        return jsonify({'error': str(e)}), 500

@contract_bp.route('/api/contract/<int:id_hop_dong>', methods=['GET'])
def get_contract(id_hop_dong):
    """
    Lấy thông tin chi tiết của một hợp đồng theo ID
    """
    try:
        contract = contract_service_get_contract_by_id(id_hop_dong)
        if contract is None:
            return jsonify({'error': 'Không tìm thấy hợp đồng'}), 404
        return jsonify(contract)
    except Exception as e:
        print(f"Error in get_contract API: {str(e)}")
        return jsonify({'error': str(e)}), 500

@contract_bp.route('/api/sharepoint-data', methods=['GET'])
def get_sharepoint_data_api():
    """
    Lấy dữ liệu từ SharePoint
    """
    try:
        data = get_sharepoint_data()
        if data is None:
            return jsonify({'error': 'Không thể lấy dữ liệu từ SharePoint'}), 500
        return jsonify(data)
    except Exception as e:
        print(f"Error in get_sharepoint_data API: {str(e)}")
        return jsonify({'error': str(e)}), 500

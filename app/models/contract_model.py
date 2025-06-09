from .database import db

# Bảng trung gian cho quan hệ nhiều-nhiều giữa hợp đồng và dịch vụ
hop_dong_dich_vu = db.Table('hop_dong_dich_vu',
    db.Column('id_hop_dong', db.Integer, db.ForeignKey('hop_dong.id_hop_dong'), primary_key=True),
    db.Column('id_dich_vu', db.Integer, db.ForeignKey('dich_vu.id_dich_vu'), primary_key=True)
)

class hopDong(db.Model):
    __tablename__ = 'hop_dong'
    id_hop_dong = db.Column(db.Integer, primary_key=True, autoincrement=True)
    ten_hop_dong = db.Column(db.String(255), nullable=False)
    ngay_ky = db.Column(db.Date, nullable=False)
    so_hop_dong = db.Column(db.String(50), nullable=False, unique=True)
    
    # Quan hệ nhiều-nhiều với dịch vụ
    dich_vu = db.relationship('dichVu', secondary=hop_dong_dich_vu, backref='hop_dong')

class dichVu(db.Model):
    __tablename__ = 'dich_vu'
    id_dich_vu = db.Column(db.Integer, primary_key=True, autoincrement=True)
    ten_dich_vu = db.Column(db.String(255), nullable=False)

class noiDungCongViec(db.Model):
    __tablename__ = 'noi_dung_cong_viec'
    id_noi_dung = db.Column(db.Integer, primary_key=True, autoincrement=True)
    ten_noi_dung = db.Column(db.String(255))
    chi_tiet = db.Column(db.Text)
    id_dich_vu = db.Column(db.Integer, db.ForeignKey('dich_vu.id_dich_vu'), nullable=False)

class quyen(db.Model):
    __tablename__ = 'quyen'
    id_quyen = db.Column(db.Integer, primary_key=True, autoincrement=True)
    chi_tiet = db.Column(db.Text, nullable=False)
    type = db.Column(db.String(1), nullable=False)  # Loại bỏ check_constraint
    id_dich_vu = db.Column(db.Integer, db.ForeignKey('dich_vu.id_dich_vu'), nullable=False)

    # Thêm kiểm tra logic nếu cần
    def validate_type(self):
        if self.type not in ['A', 'B']:
            raise ValueError("Type must be 'A' or 'B'")

class nghiaVu(db.Model):
    __tablename__ = 'nghia_vu'
    id_nghia_vu = db.Column(db.Integer, primary_key=True, autoincrement=True)
    chi_tiet = db.Column(db.Text, nullable=False)
    type = db.Column(db.String(1), nullable=False)  # Loại bỏ check_constraint
    id_dich_vu = db.Column(db.Integer, db.ForeignKey('dich_vu.id_dich_vu'), nullable=False)

    # Thêm kiểm tra logic nếu cần
    def validate_type(self):
        if self.type not in ['A', 'B']:
            raise ValueError("Type must be 'A' or 'B'")

class phuongThucThanhToan(db.Model):
    __tablename__ = 'phuong_thuc_thanh_toan'
    id_pt_thanh_toan = db.Column(db.Integer, primary_key=True, autoincrement=True)
    chi_tiet = db.Column(db.Text, nullable=False)
    id_dich_vu = db.Column(db.Integer, db.ForeignKey('dich_vu.id_dich_vu'), nullable=False)

class phiDichVu(db.Model):
    __tablename__ = 'phi_dich_vu'
    id_phi_dv = db.Column(db.Integer, primary_key=True, autoincrement=True)
    chi_tiet = db.Column(db.Text, nullable=False)
    id_dich_vu = db.Column(db.Integer, db.ForeignKey('dich_vu.id_dich_vu'), nullable=False)

-- PROJECT MILESTONE: LTO INFORMATION MANAGEMENT SYSTEM
-- ==============================================================================

-- 1. DATABASE SETUP
-- ==============================================================================
CREATE OR REPLACE USER 'lto'@'localhost' IDENTIFIED BY 'lto';
DROP DATABASE IF EXISTS `trafficdb`;
CREATE DATABASE IF NOT EXISTS `trafficdb`;
GRANT ALL ON trafficdb.* TO 'lto'@'localhost';
USE `trafficdb`;


-- 2. TABLE CREATION 
-- ==============================================================================

-- DRIVER TABLE
CREATE TABLE `driver` (
  `license_number` varchar(15) NOT NULL,
  `full_name` varchar(100) NOT NULL,
  `birthdate` date,
  `sex` varchar(10),
  `address` varchar(255),
  `license_type` varchar(20),
  `license_expiry` date,
  `license_issuance` date,
  `license_status` ENUM('Valid','Expired','Suspended','Revoked') NOT NULL, 
  PRIMARY KEY (`license_number`)
) ENGINE=InnoDB;

-- VEHICLE TABLE
CREATE TABLE `vehicle` (
  `plate_number` varchar(20) NOT NULL,
  `engine_number` varchar(30) UNIQUE,
  `chassis_number` varchar(17) UNIQUE,
  `vehicle_type` varchar(50),
  `make` varchar(50),
  `model` varchar(50),
  `year` int,
  `color` varchar(30),
  `license_number` varchar(15),
  PRIMARY KEY (`plate_number`),
  FOREIGN KEY (`license_number`) REFERENCES `driver`(`license_number`)
) ENGINE=InnoDB;

-- TRAFFIC VIOLATIONS TABLE
CREATE TABLE `traffic_violation` (
  `violation_id` int AUTO_INCREMENT,
  `date` date,
  `location` varchar(255),
  `fine_amount` decimal(10,2),
  `violation_type` varchar(100),
  `apprehending_officer` varchar(100),
  `violation_status` varchar(50),
  `license_number` varchar(15),
  `plate_number` varchar(20),
  PRIMARY KEY (`violation_id`),
  FOREIGN KEY (`license_number`) REFERENCES `driver`(`license_number`),
  FOREIGN KEY (`plate_number`) REFERENCES `vehicle`(`plate_number`)
) ENGINE=InnoDB;

-- VEHICLE REGISTRATION TABLE
CREATE TABLE `vehicle_registration` (
  `registration_number` varchar(30),
  `registration_status` ENUM('Active','Expired','Suspended') NOT NULL,
  `registration_date` date,
  `expiration_date` date,
  `plate_number` varchar(20),
  PRIMARY KEY (`registration_number`),
  FOREIGN KEY (`plate_number`) REFERENCES `vehicle`(`plate_number`)
) ENGINE=InnoDB;

-- 3. MOCK DATA INSERTION
-- ==============================================================================

-- Insert Drivers (LTO Format: A01-23-456789)
INSERT INTO `driver` VALUES
('N01-22-123456','Von Michael Arellano','1998-04-10','Male','Taguig City, Metro Manila','Non-Professional','2032-05-10','2022-05-10','Valid'),
('N02-21-654321','Maria Erika Dominique Cunanan','1995-07-22','Female','Pasig City, Metro Manila','Professional','2031-07-22','2021-07-22','Valid'),
('C03-20-112233','Carl Angelo Angcana','1994-01-15','Male','Caloocan City, Metro Manila','Professional','2030-03-15','2020-03-15','Valid'),
('M04-24-998877','Abigail Nadua','1999-07-22','Female','Manila City, Metro Manila','Non-Professional','2034-06-19','2024-06-19','Valid'),
('R05-20-445566','John Michael Raqueño','1997-08-09','Male','Antipolo City, Rizal','Student Permit','2021-08-09','2020-08-09','Revoked'),
('B06-25-778899','Mylah Rystie Anacleto','1978-12-01','Female','Baguio City, Benguet','Professional','2030-12-01','2025-12-01','Valid'),
('I07-22-334455','Reginald Neil Recario','1989-06-25','Male','Iloilo City, Iloilo','Professional','2032-06-25','2022-06-25','Valid'),
('M08-20-667788','Danielle Lei Araez','2000-02-14','Female','Manila City, Metro Manila','Student Permit','2021-02-14','2020-02-14','Suspended'),
('N09-23-223344','Andre Tuazon','1998-02-11','Male','Pasig City, Metro Manila','Professional','2033-02-11','2023-02-11','Valid'),
('L10-21-556677','Ariel Doria','1994-08-09','Male','Calamba City, Laguna','Non-Professional','2031-08-09','2021-08-09','Valid'),
('B11-19-889900','Jaderick Pabico','1969-04-03','Male','Bacolod City, Negros Occidental','Professional','2024-04-03','2019-04-03','Suspended'),
('C12-24-111222','Shanmykel Ace Dela Cruz','1999-02-20','Male','Cebu City, Cebu','Professional','2034-02-20','2024-02-20','Valid'),
('N13-23-333444','Zenith Arnejo','1988-09-09','Female','Pasay City, Metro Manila','Non-Professional','2033-09-09','2023-09-09','Valid'),
('C14-21-555666','Aldrin Joseph Hao','1971-06-14','Male','Imus, Cavite','Professional','2026-06-14','2021-06-14','Suspended'),
('L15-25-777888','Leonard Paul Garchitorena','1997-12-03','Male','Santa Rosa City, Laguna','Non-Professional','2035-12-03','2025-12-03','Valid'),
('T16-25-999000','Prince Karlo Aragones','1994-01-25','Male','Tacloban City, Leyte','Student Permit','2026-01-25','2025-01-25','Expired'),
('Z17-20-222333','Jamlech Iram Gojo Cruz','1995-03-03','Male','Zamboanga City, Zamboanga del Sur','Professional','2030-03-03','2020-03-03','Valid'),
('P18-22-444555','Rizza Mercado','1976-07-07','Female','Puerto Princesa City, Palawan','Non-Professional','2032-07-07','2022-07-07','Valid'),
('Q19-24-666777','Aaron Carl Maaño','2000-05-12','Male','Quezon City, Metro Manila','Non-Professional','2034-05-12','2024-05-12','Valid'),
('N20-21-888999','Arvin Kent Jacob','1999-06-20','Male','Pasig City, Metro Manila','Professional','2031-06-20','2021-06-20','Valid'),
('B21-20-123123','Daryll Dan Caponpon','2001-09-17','Male','Batangas City, Batangas','Student Permit','2021-09-17','2020-09-17','Expired'),
('L22-23-456456','Iravan Gesmundo','1998-12-08','Male','Biñan City, Laguna','Non-Professional','2033-12-08','2023-12-08','Valid'),
('C23-20-789789','Jarem Thimoty Arias','1999-11-11','Male','Dasmariñas City, Cavite','Non-Professional','2030-11-11','2020-11-11','Valid'),
('B24-22-321321','John Cristopher Angeles','1998-04-04','Male','Malolos City, Bulacan','Professional','2032-04-04','2022-04-04','Valid'),
('R25-24-654654','Janzelle Arman Servanda','1999-01-21','Male','Taytay, Rizal','Student Permit','2025-01-21','2024-01-21','Valid'),
('C26-20-987987','Arian Jacildo','1965-03-03','Male','Cebu City, Cebu','Professional','2025-03-03','2020-03-03','Revoked'),
('I27-21-147147','Fermin Roberto Lapitan','1966-07-07','Male','Laoag City, Ilocos Norte','Professional','2031-07-07','2021-07-07','Valid'),
('D28-22-258258','Joseph Anthony Hermocilla','1960-06-06','Male','Davao City, Davao del Sur','Professional','2032-06-06','2022-06-06','Valid'),
('L29-23-369369','Juan Miguel Bawagan','1995-09-09','Male','San Pablo City, Laguna','Professional','2033-09-09','2023-09-09','Valid'),
('B30-19-159159','Rodolfo Camaclang','1986-01-01','Male','Balanga City, Bataan','Professional','2024-01-01','2019-01-01','Expired');

-- Insert Vehicles
INSERT INTO `vehicle` VALUES
('ABC123','1NZ-FE 8392012','JH4KA9650MC012345','Car','Toyota','Vios',2022,'Red','N01-22-123456'),
('ABC124','2GD-FTV 5567123','MMDAA12ZXKH123456','SUV','Toyota','Fortuner',2023,'Black','N01-22-123456'),
('YTR118','D4HB-6655442','KMHSN81XADU456789','SUV','Hyundai','Santa Fe',2022,'White','N01-22-123456'),
('XYZ789','ESP150-9988776','MLHJFZ123PK567890','Motorcycle','Honda','Click',2023,'Black','N02-21-654321'),
('JQX491','1KR-FE 1122445','MHKP3BA2XJK123456','Car','Toyota','Wigo',2023,'White','N02-21-654321'),
('NVR208','4N15-6677554','MMTHA4CU0KH654321','SUV','Mitsubishi','Montero',2022,'Black','C03-20-112233'),
('LMN456','4JJ1-TC 3344556','JALB4B165J7001234','Truck','Isuzu','N-Series',2021,'White','C03-20-112233'),
('DEF321','3A92-2233445','MMSXTA03AEH045678','Car','Mitsubishi','Mirage',2024,'Blue','M04-24-998877'),
('KLT774','KF18-8899776','MLHJFZ111PK222333','Motorcycle','Honda','ADV160',2024,'Red','M04-24-998877'),
('GHI654','YS23-7788991','MAJAXXMRKAFD12345','SUV','Ford','Everest',2023,'Gray','R05-20-445566'),
('JKL987','G3C1E-4455667','ME4JFZ987LK345678','Motorcycle','Yamaha','NMAX',2022,'White','B06-25-778899'),
('MNO741','1KD-FTV 8899001','JTFHT02P0XH567890','Van','Toyota','Hiace',2024,'Silver','I07-22-334455'),
('PDM563','6HK1-2233557','JALFTR34XJ7004567','Truck','Isuzu','Forward',2021,'Blue','I07-22-334455'),
('PQR852','L15Z1-1122334','MRHGM2620NP012345','Car','Honda','City',2022,'Blue','M08-20-667788'),
('STU963','HR12DE-5566778','MNTCB3D23Z0123456','Car','Nissan','Almera',2023,'Red','N09-23-223344'),
('XCY902','1KD-FTV 4433556','JTFST22P0MH987654','Van','Toyota','Hiace',2023,'Silver','N09-23-223344'),
('RTA615','QR25DE-7788992','JN1CV6AR5BM765432','Car','Nissan','Altima',2022,'Gray','L10-21-556677'),
('VWX147','R150-3344556','LC6PCJG94H0012345','Motorcycle','Suzuki','Raider',2021,'Black','L10-21-556677'),
('YZA258','G4NA-6677889','KMHJT81BADU123456','SUV','Hyundai','Tucson',2024,'White','B11-19-889900'),
('BCD369','G4LC-9988776','KNADM412BPT654321','Car','Kia','Soluto',2022,'Gray','C12-24-111222'),
('BLF338','155FMI-8899002','ME4KC1234LK876543','Motorcycle','Yamaha','Sniper',2023,'Black','C12-24-111222'),
('EFG111','2ZR-FE 5544332','JTDBU4EE9AJ012345','Car','Toyota','Corolla',2023,'White','N13-23-333444'),
('EFG112','1.5T-8877665','MAJ6S3KL0MC123456','SUV','Ford','Territory',2024,'Black','N13-23-333444'),
('UWN451','2.3L-ECO 4455667','1FM5K8GT0MGB12345','SUV','Ford','Explorer',2024,'White','N13-23-333444'),
('HIJ222','ESP125-2211334','MLHJFZ765LK987654','Motorcycle','Honda','Beat',2022,'Red','C14-21-555666'),
('KLM333','K10B-6655443','MA3ETDE1S00234567','Car','Suzuki','Celerio',2021,'Blue','L15-25-777888'),
('QZE129','G4FG-1122335','KNADN4A31C6123456','Car','Kia','Rio',2021,'Blue','L15-25-777888'),
('NOP444','YD25-4433221','JN1TCS4E0HU567890','Van','Nissan','Urvan',2024,'Silver','T16-25-999000'),
('QRS555','2NR-FE 7788990','JTMH43FV80D123456','SUV','Toyota','Rush',2023,'Gray','Z17-20-222333'),
('HSP667','D4CB-6677881','KMJWA37HBCU765432','Van','Hyundai','Starex',2022,'Black','Z17-20-222333'),
('MKA842','UH125-5566771','LC6PGM987H0012346','Motorcycle','Suzuki','Burgman',2023,'Gray','P18-22-444555'),
('TUV666','G3F1E-9988001','ME1SG1234LK567890','Motorcycle','Yamaha','Aerox',2023,'Black','P18-22-444555'),
('WXY777','K20C1-5566443','MRHFK5660DP123456','Car','Honda','Civic',2022,'Red','Q19-24-666777'),
('BVC773','KF18-4455661','MLHJK1234PK567890','Motorcycle','Honda','PCX160',2024,'Black','Q19-24-666777'),
('ZAB888','4JJ1-3344221','JALC4W166H7009876','Truck','Isuzu','Elf',2020,'White','N20-21-888999'),
('DPL390','6WG1-3344552','JALGG8J18H7001122','Truck','Isuzu','Giga',2020,'White','N20-21-888999'),
('ZRT555','L12B-8877664','MRHDD1830DP345678','Car','Honda','Brio',2024,'Red','L22-23-456456'),
('WQP731','1KR-VET 2233446','MHKAB12A0LK234567','SUV','Toyota','Raize',2023,'Yellow','C23-20-789789'),
('CNM284','BC175-7788993','MD2A18AY6PK123456','Motorcycle','Kawasaki','Barako',2022,'Green','B24-22-321321'),
('REV101','D16W-9988771','JH4DB8590SS123456','Car','Honda','Civic',2020,'Black','C26-20-987987'),
('LXO918','PUJ-1122334','JEEPNEY1234567890','Jeepney','Sarao','Traditional',2019,'Multicolor','I27-21-147147'),
('TRI204','TVS175-5566772','TRICYCLE123456789','Tricycle','TVS','King',2021,'Blue','D28-22-258258'),
('FGE660','PE-VPS 9988772','JM1BPACL0P1234567','Car','Mazda','3',2023,'Red','L29-23-369369');


-- Insert Traffic Violations 
INSERT INTO `traffic_violation` 
(`date`,`location`,`fine_amount`,`violation_type`,`apprehending_officer`,`violation_status`,`license_number`,`plate_number`) VALUES

--  VEHICLE: ABC123 | Driver: N01-22-123456 (Von Michael Arellano)
('2024-02-10','C5 Taguig',1500,'Overspeeding','Officer Cruz','Unpaid','N01-22-123456','ABC123'),
('2024-02-10','C5 Taguig',1000,'No Seatbelt','Officer Cruz','Unpaid','N01-22-123456','ABC123'),
('2025-01-15','EDSA Makati',2000,'Swerving','Officer Mendoza','Paid','N01-22-123456','ABC123'),

--  VEHICLE: YTR118 | Driver: N01-22-123456 (Von Michael Arellano)
('2025-06-18','BGC Taguig',1000,'Illegal Parking','Officer Santos','Paid','N01-22-123456','YTR118'),

--  VEHICLE: XYZ789 | Driver: N02-21-654321 (Maria Erika Dominique Cunanan)
('2024-05-21','Ortigas Pasig',1000,'Illegal Parking','Officer Santos','Paid','N02-21-654321','XYZ789'),
('2026-02-14','C5 Pasig',1700,'Overspeeding','Officer Cruz','Unpaid','N02-21-654321','XYZ789'),
('2026-02-14','C5 Pasig',1000,'No Helmet','Officer Cruz','Unpaid','N02-21-654321','XYZ789'),

--  VEHICLE: LMN456 | Driver: C03-20-112233 (Carl Angelo Angcana)
('2024-08-14','NLEX',2000,'Reckless Driving','Officer Reyes','Unpaid','C03-20-112233','LMN456'),
('2024-08-14','NLEX',2500,'Overloading','Officer Reyes','Unpaid','C03-20-112233','LMN456'),

--  VEHICLE: GHI654 | Driver: R05-20-445566 (John Michael Raqueño - Revoked)
('2025-03-11','Marcos Highway Antipolo',1800,'Overspeeding','Officer Lim','Unpaid','R05-20-445566','GHI654'),
('2025-03-11','Marcos Highway Antipolo',3000,'Driving Without Valid License','Officer Lim','Unpaid','R05-20-445566','GHI654'),

--  VEHICLE: DEF321 | Driver: M08-20-667788 (Danielle Lei Araez - Suspended)
('2026-01-05','Taft Avenue Manila',2500,'Reckless Driving','Officer Ramos','Unpaid','M08-20-667788','DEF321'),
('2026-01-05','Taft Avenue Manila',1800,'Overspeeding','Officer Ramos','Unpaid','M08-20-667788','DEF321'),
('2026-02-20','Roxas Blvd Manila',1000,'Disregarding Traffic Sign','Officer Ramos','Unpaid','M08-20-667788','DEF321'),

--  VEHICLE: VWX147 | Driver: L10-21-556677 (Ariel Doria)
('2025-06-05','SLEX Calamba',1500,'Illegal Parking','Officer Santos','Paid','L10-21-556677','VWX147'),
('2026-03-01','SLEX Laguna',1000,'No Helmet','Officer Garcia','Paid','L10-21-556677','VWX147'),

--  VEHICLE: YZA258 | Driver: B11-19-889900 (Jaderick Pabico - Suspended)
('2024-11-20','Bacolod City',2000,'Reckless Driving','Officer Reyes','Unpaid','B11-19-889900','YZA258'),
('2024-11-20','Bacolod City',1500,'Overspeeding','Officer Reyes','Unpaid','B11-19-889900','YZA258'),

--  VEHICLE: HIJ222 | Driver: C14-21-555666 (Aldrin Joseph Hao - Suspended)
('2024-04-18','Aguinaldo Highway Cavite',1500,'Overspeeding','Officer Santos','Unpaid','C14-21-555666','HIJ222'),
('2024-04-18','Aguinaldo Highway Cavite',2500,'Reckless Driving','Officer Santos','Unpaid','C14-21-555666','HIJ222'),

--  VEHICLE: NOP444 | Driver: T16-25-999000 (Prince Karlo Aragones - Expired)
('2026-02-01','Tacloban City',2000,'Driving with Expired License','Officer Garcia','Unpaid','T16-25-999000','NOP444'),

--  VEHICLE: ZAB888 | Driver: N20-21-888999 (Arvin Kent Jacob)
('2025-08-14','C5 Pasig',2100,'Reckless Driving','Officer Cruz','Unpaid','N20-21-888999','ZAB888'),

--  VEHICLE: DPL390 | Driver: N20-21-888999 (Arvin Kent Jacob)
('2025-08-14','C5 Pasig',2500,'Overloading','Officer Cruz','Unpaid','N20-21-888999','DPL390'),

--  VEHICLE: REV101 | Driver: C26-20-987987 (Arian Jacildo - Revoked)
('2024-06-15','Cebu City',3000,'Driving Without Valid License','Officer Cruz','Unpaid','C26-20-987987','REV101'),
('2024-06-15','Cebu City',2000,'Reckless Driving','Officer Cruz','Unpaid','C26-20-987987','REV101'),
('2024-06-15','Cebu City',10000,'Unregistered Vehicle','Officer Cruz','Unpaid','C26-20-987987','REV101'),

--  VEHICLE: MNO741 | Driver: I07-22-334455 (Reginald Neil Recario)
('2025-07-19','Iloilo City',900,'No Seatbelt','Officer Tan','Paid','I07-22-334455','MNO741'),

--  VEHICLE: EFG111 | Driver: N13-23-333444 (Zenith Arnejo)
('2024-01-12','Pasay City',1000,'Illegal Parking','Officer Cruz','Paid','N13-23-333444','EFG111'),

--  VEHICLE: QRS555 | Driver: Z17-20-222333 (Jamlech Iram Gojo Cruz)
('2025-02-11','Zamboanga City',1700,'Overspeeding','Officer Lim','Unpaid','Z17-20-222333','QRS555'),

--  VEHICLE: TUV666 | Driver: P18-22-444555 (Rizza Mercado)
('2025-03-19','Puerto Princesa',900,'No Helmet','Officer Tan','Paid','P18-22-444555','TUV666'),

--  VEHICLE: WXY777 | Driver: Q19-24-666777 (Aaron Carl Maaño)
('2025-05-22','Quezon City',1300,'Illegal Parking','Officer Ramos','Paid','Q19-24-666777','WXY777');


-- Insert Vehicle Registrations 
INSERT INTO `vehicle_registration` VALUES
('1301-00000012345','Expired','2023-01-01','2024-01-01','ABC123'),
('1301-00000022346','Expired','2024-01-01','2025-01-01','ABC123'),
('1301-00000032347','Active','2025-01-01','2026-01-01','ABC123'),

('1301-00000099999','Active','2025-01-01','2026-01-01','YTR118'),

('1301-00000042348','Active','2025-03-01','2026-03-01','ABC124'),

('0403-0000204730','Expired','2024-03-15','2025-03-15','XYZ789'),
('0403-0000204731','Active','2025-03-15','2026-03-15','XYZ789'),

('0403-0000204732','Active','2025-06-01','2026-06-01','JQX491'),

('0201-0000101111','Active','2025-05-01','2026-05-01','NVR208'),

('0201-0000101112','Expired','2024-06-10','2025-06-10','LMN456'),
('0201-0000101113','Active','2025-06-10','2026-06-10','LMN456'),

('0401-0000300001','Active','2025-02-20','2026-02-20','DEF321'),

('0401-0000300002','Active','2025-03-10','2026-03-10','KLT774'),

('0308-0000400001','Expired','2023-09-01','2024-09-01','GHI654'),

('1501-0000500001','Active','2025-05-12','2026-05-12','JKL987'),

('0601-0000600001','Active','2026-01-01','2027-01-01','MNO741'),

('0601-0000600002','Active','2025-08-08','2026-08-08','PDM563'),

('0701-0000700001','Suspended','2025-08-08','2026-08-08','PQR852'),

('0403-0000204733','Active','2025-02-01','2026-02-01','STU963'),

('0403-0000204734','Active','2025-03-01','2026-03-01','XCY902'),

('0405-0000800001','Active','2025-05-05','2026-05-05','RTA615'),

('0405-0000800002','Active','2025-05-05','2026-05-05','VWX147'),

('1001-0000900001','Suspended','2025-01-01','2026-01-01','YZA258'),

('1301-00000052349','Active','2025-02-02','2026-02-02','BCD369'),

('1301-00000052350','Active','2025-03-03','2026-03-03','BLF338'),

('1301-00000052351','Expired','2024-02-02','2025-02-02','EFG111'),
('1301-00000052352','Active','2025-02-02','2026-02-02','EFG111'),

('1301-00000052353','Active','2025-03-03','2026-03-03','EFG112'),

('1301-00000052354','Active','2025-04-04','2026-04-04','UWN451'),

('1302-00000060001','Suspended','2025-04-04','2026-04-04','HIJ222'),

('0402-0000700002','Active','2025-05-05','2026-05-05','KLM333'),

('0402-0000700003','Active','2025-06-06','2026-06-06','QZE129'),

('0801-0000800001','Expired','2024-07-07','2025-07-07','NOP444'),

('0901-0000900002','Active','2025-07-07','2026-07-07','QRS555'),

('0901-0000900003','Active','2025-07-07','2026-07-07','HSP667'),

('1701-0001000001','Active','2025-01-01','2026-01-01','MKA842'),

('1701-0001000002','Active','2025-01-01','2026-01-01','TUV666'),

('1601-0001100001','Active','2025-02-02','2026-02-02','WXY777'),

('1601-0001100002','Active','2025-03-03','2026-03-03','BVC773'),

('1201-0001200001','Active','2025-01-01','2026-01-01','ZAB888'),

('1201-0001200002','Active','2025-01-01','2026-01-01','DPL390'),

('0401-0000300003','Active','2025-03-03','2026-03-03','ZRT555'),

('0401-0000300004','Active','2025-04-04','2026-04-04','WQP731'),

('0301-0000400002','Active','2025-05-05','2026-05-05','CNM284'),

('0101-0000500002','Active','2025-06-06','2026-06-06','LXO918'),

('0102-0000500003','Active','2025-07-07','2026-07-07','TRI204'),

('1101-0000600003','Active','2025-08-08','2026-08-08','FGE660');



-- 4. DATABASE OBJECTS (Views, Procedures, Triggers)
-- ==============================================================================

-- VIEW 1: Active Professional Male Drivers aged 25-40
CREATE OR REPLACE VIEW `vw_active_pro_male_drivers` AS
SELECT 
    license_number, full_name, birthdate, sex, address, license_type, license_status, 
    TIMESTAMPDIFF(YEAR, birthdate, CURDATE()) AS age
FROM driver 
WHERE license_type = 'Professional' 
  AND license_status = 'Active' 
  AND sex = 'Male' 
  AND TIMESTAMPDIFF(YEAR, birthdate, CURDATE()) BETWEEN 25 AND 40;

-- VIEW 2: Drivers with expired, suspended, or revoked licenses
CREATE OR REPLACE VIEW `vw_inactive_drivers` AS
SELECT 
    license_number, full_name, license_type, license_status, license_expiry
FROM driver
WHERE license_status IN ('Expired', 'Suspended', 'Revoked');

DELIMITER //

-- PROCEDURE 1: View all vehicles owned by a given driver
CREATE PROCEDURE `GetVehiclesByDriver` (IN p_license_number VARCHAR(15))
BEGIN
    SELECT d.full_name, v.plate_number, v.vehicle_type, v.make, v.model, v.year, v.color
    FROM vehicle v
    JOIN driver d ON v.license_number = d.license_number
    WHERE d.license_number = p_license_number;
END //

-- PROCEDURE 2: View all vehicles with expired registrations as of a given date
CREATE PROCEDURE `GetExpiredRegistrationsAsOf` (IN p_target_date DATE)
BEGIN
    SELECT v.plate_number, v.make, v.model, vr.registration_number, vr.expiration_date, vr.registration_status
    FROM vehicle v
    JOIN vehicle_registration vr ON v.plate_number = vr.plate_number
    WHERE vr.expiration_date < p_target_date 
      AND vr.registration_status = 'Expired';
END //

-- PROCEDURE 3: View all traffic violations committed by a given driver within a date range
CREATE PROCEDURE `GetDriverViolationsByDate` (
    IN p_license_number VARCHAR(15), 
    IN p_start_date DATE, 
    IN p_end_date DATE
)
BEGIN
    SELECT violation_id, date, location, violation_type, fine_amount, violation_status
    FROM traffic_violation
    WHERE license_number = p_license_number 
      AND date BETWEEN p_start_date AND p_end_date;
END //

-- PROCEDURE 4: View the total number of violations per violation type for a given year
CREATE PROCEDURE `GetViolationStatsByYear` (IN p_year INT)
BEGIN
    SELECT violation_type, COUNT(*) AS total_violations
    FROM traffic_violation
    WHERE YEAR(date) = p_year
    GROUP BY violation_type
    ORDER BY total_violations DESC;
END //

-- PROCEDURE 5: View all vehicles involved in violations within a given city or region
CREATE PROCEDURE `GetViolationsByLocation` (IN p_location VARCHAR(100))
BEGIN
    SELECT DISTINCT v.plate_number, v.make, v.model, tv.date, tv.violation_type, tv.location
    FROM vehicle v
    JOIN traffic_violation tv ON v.plate_number = tv.plate_number
    WHERE tv.location LIKE CONCAT('%', p_location, '%');
END //

-- TRIGGER: Ensure data integrity by automatically setting past dates to Expired
CREATE TRIGGER `trg_check_registration_expiry`
BEFORE INSERT ON `vehicle_registration`
FOR EACH ROW
BEGIN
    IF NEW.expiration_date < CURDATE() THEN
        SET NEW.registration_status = 'Expired';
    END IF;
END //

DELIMITER ;
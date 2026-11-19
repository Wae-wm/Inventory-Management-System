-- ให้ stock_movements เก็บการปรับยอด (ADJUSTMENT) เป็นจำนวนติดลบได้
-- เดิม CHECK บังคับ quantity > 0 ทำให้บอกไม่ได้ว่าการปรับยอดเป็นการเพิ่มหรือลด
-- กฎใหม่: IN/OUT ต้องเป็นบวก, ADJUSTMENT ต้องไม่เป็น 0 (บวก = เพิ่ม, ลบ = ลด)
USE inventory_db;

ALTER TABLE stock_movements DROP CHECK chk_movement_quantity;

ALTER TABLE stock_movements
  ADD CONSTRAINT chk_movement_quantity CHECK (
    (movement_type = 'ADJUSTMENT' AND quantity <> 0)
    OR (movement_type <> 'ADJUSTMENT' AND quantity > 0)
  );

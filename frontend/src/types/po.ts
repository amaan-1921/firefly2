export type PoStatus =
  | 'OPEN'
  | 'IN_TRANSIT'
  | 'DELAYED'
  | 'CANCELLED'
  | 'CLOSED';

export interface PO {
  id: string;
  poNumber: string;
  supplierId: string;
  supplierName: string;
  item: string;
  quantity: number;
  dueDate: string;
  currency: string;
  financialImpact: number;
  status: PoStatus;
  alertIds: string[];
}

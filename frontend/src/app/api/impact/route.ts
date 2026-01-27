// src/app/api/impact/route.ts
import { NextRequest, NextResponse } from 'next/server';
import { faker } from '@faker-js/faker';
import type { PO } from '@/types/po';

function generatePO(alertId: string): PO {
  const supplierId = faker.string.uuid();
  const financialImpact = faker.number.int({ min: 50_000, max: 2_000_000 });

  return {
    id: faker.string.uuid(),
    poNumber: `PO-${faker.number.int({ min: 100000, max: 999999 })}`,
    supplierId,
    supplierName: faker.company.name(),
    item: faker.commerce.productName(),
    quantity: faker.number.int({ min: 1000, max: 50000 }),
    dueDate: faker.date.future().toISOString().slice(0, 10),
    currency: 'USD',
    financialImpact,
    status: 'DELAYED',
    alertIds: [alertId]
  };
}

export async function GET(req: NextRequest) {
  const { searchParams } = new URL(req.url);
  const alertId = searchParams.get('alertId');

  if (!alertId) {
    return NextResponse.json([], { status: 200 });
  }

  if (process.env.BACKEND_URL) {
    // TODO: proxy to real backend
    // const res = await fetch(
    //   `${process.env.BACKEND_URL}/impact?alertId=${alertId}`
    // );
    // const data = await res.json();
    // return NextResponse.json(data);
  }

  const pos: PO[] = faker.helpers.multiple(
    () => generatePO(alertId),
    { count: 5 }
  );

  return NextResponse.json(pos);
}

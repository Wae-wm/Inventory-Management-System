export const num = (v) => Number(v).toLocaleString("th-TH");
export const money = (v) =>
  Number(v).toLocaleString("th-TH", { minimumFractionDigits: 2, maximumFractionDigits: 2 });
export const dateTime = (s) =>
  new Date(s).toLocaleString("th-TH", { dateStyle: "short", timeStyle: "short" });

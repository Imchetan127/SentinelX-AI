/**
 * Standardized Date and Time formatting utility for SentinelX AI.
 * 
 * Standard Format Requirement:
 *   "08 Aug 2026 • 21:02:24 IST"
 * 
 * Live SOC Clock Requirement:
 *   "Saturday, 08 August 2026"
 *   "21:02:24 IST"
 */

export function formatStandardDate(input?: string | number | Date | null): string {
  if (!input) {
    return formatSingleDate(new Date());
  }

  const d = new Date(input);
  if (isNaN(d.getTime())) {
    // If string already contains a formatted date or custom log string, return as is or wrap
    return String(input);
  }

  return formatSingleDate(d);
}

function formatSingleDate(d: Date): string {
  const day = d.getDate().toString().padStart(2, '0');
  const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
  const month = months[d.getMonth()];
  const year = d.getFullYear();

  const hours = d.getHours().toString().padStart(2, '0');
  const minutes = d.getMinutes().toString().padStart(2, '0');
  const seconds = d.getSeconds().toString().padStart(2, '0');

  let tzStr = 'IST';
  try {
    const parts = Intl.DateTimeFormat('en-US', { timeZoneName: 'short' }).formatToParts(d);
    const tzPart = parts.find(p => p.type === 'timeZoneName');
    if (tzPart && tzPart.value) {
      tzStr = tzPart.value;
    }
  } catch {
    tzStr = 'IST';
  }

  return `${day} ${month} ${year} • ${hours}:${minutes}:${seconds} ${tzStr}`;
}

export function formatSocClock(d = new Date()) {
  const days = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];
  const months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'];

  const dayOfWeek = days[d.getDay()];
  const day = d.getDate().toString().padStart(2, '0');
  const monthName = months[d.getMonth()];
  const year = d.getFullYear();

  const hours = d.getHours().toString().padStart(2, '0');
  const minutes = d.getMinutes().toString().padStart(2, '0');
  const seconds = d.getSeconds().toString().padStart(2, '0');

  let tzStr = 'IST';
  try {
    const parts = Intl.DateTimeFormat('en-US', { timeZoneName: 'short' }).formatToParts(d);
    const tzPart = parts.find(p => p.type === 'timeZoneName');
    if (tzPart && tzPart.value) {
      tzStr = tzPart.value;
    }
  } catch {
    tzStr = 'IST';
  }

  return {
    dayOfWeek,
    dateStr: `${day} ${monthName} ${year}`,
    timeStr: `${hours}:${minutes}:${seconds}`,
    tzStr,
    formattedDate: `${dayOfWeek}, ${day} ${monthName} ${year}`,
    formattedTime: `${hours}:${minutes}:${seconds} ${tzStr}`,
    full: `${dayOfWeek}, ${day} ${monthName} ${year} • ${hours}:${minutes}:${seconds} ${tzStr}`
  };
}

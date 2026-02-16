/**
 * Format a large number as currency with suffixes (K, M, B, T)
 * @param {number} value - The value to format
 * @param {boolean} showCurrencySymbol - Whether to show the currency symbol
 * @returns {string} Formatted string
 */
export function formatLargeCurrency(value, showCurrencySymbol = true) {
    if (value === null || value === undefined) return '-';

    // Handle strings that might be passed accidentally
    const num = Number(value);
    if (isNaN(num)) return '-';

    const symbol = showCurrencySymbol ? '$' : '';
    const absValue = Math.abs(num);

    if (absValue >= 1e12) {
        return `${symbol}${(num / 1e12).toFixed(2)}T`;
    }
    if (absValue >= 1e9) {
        return `${symbol}${(num / 1e9).toFixed(2)}B`;
    }
    if (absValue >= 1e6) {
        return `${symbol}${(num / 1e6).toFixed(2)}M`;
    }
    if (absValue >= 1e3) {
        return `${symbol}${(num / 1e3).toFixed(2)}K`;
    }

    return `${symbol}${num.toFixed(2)}`;
}

/**
 * Format a date string or object to the user's local timezone
 * @param {string|Date|number} dateInput - The date to format
 * @param {boolean} includeYear - Whether to include the year in the output
 * @returns {string} Formatted date string
 */
export function formatLocal(dateInput, includeYear = true) {
    if (!dateInput) return '—';

    try {
        let dateObj;
        if (dateInput instanceof Date) {
            dateObj = dateInput;
        } else if (typeof dateInput === 'string') {
            // Check if it's already a format the browser knows well (like RFC 1123 from backend)
            // or if it already has timezone information.
            const hasTimezone = dateInput.endsWith('Z') ||
                dateInput.includes('GMT') ||
                dateInput.includes('UTC') ||
                /[+-]\d{2}:?\d{2}$/.test(dateInput);

            if (hasTimezone || dateInput.includes(',')) {
                // It's likely an RFC 1123 string or has an offset/Z already
                dateObj = new Date(dateInput);
            } else {
                // It's a "naked" ISO string (e.g. "2026-02-16 17:29" or "2026-02-16T17:29")
                // Replace space with T for browser compatibility
                let normalized = dateInput.replace(' ', 'T');
                // Append Z to force UTC if no other TZ info is present
                if (!normalized.endsWith('Z')) {
                    normalized += 'Z';
                }
                dateObj = new Date(normalized);
            }
        } else {
            dateObj = new Date(dateInput);
        }

        if (isNaN(dateObj.getTime())) return 'Invalid Date';

        return dateObj.toLocaleString('en-US', {
            month: 'short',
            day: 'numeric',
            year: includeYear ? 'numeric' : undefined,
            hour: 'numeric',
            minute: '2-digit',
            hour12: false
        });
    } catch (e) {
        console.error("Format error:", e);
        return 'Invalid Date';
    }
}

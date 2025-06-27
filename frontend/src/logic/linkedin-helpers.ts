/**
 * Formats a date string (e.g., "Today", "Yesterday", "Monday", "Jan 30")
 * into a standardized "YYYY-MM-DD" format.
 * @param dateStr The date string from the LinkedIn UI.
 * @returns A formatted "YYYY-MM-DD" string.
 */
export function getFormattedDate(dateStr: string): string {
    const now = new Date();
    const year = now.getFullYear();

    const toYyyyMmDd = (d: Date): string => {
        const month = String(d.getMonth() + 1).padStart(2, '0');
        const day = String(d.getDate()).padStart(2, '0');
        return `${d.getFullYear()}-${month}-${day}`;
    };

    if (dateStr.toLowerCase() === 'today') {
        return toYyyyMmDd(now);
    }
    
    if (dateStr.toLowerCase() === 'yesterday') {
        const yesterday = new Date();
        yesterday.setDate(now.getDate() - 1);
        return toYyyyMmDd(yesterday);
    }

    const daysOfWeek = ['sunday', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday'];
    const dayIndex = daysOfWeek.indexOf(dateStr.toLowerCase());

    if (dayIndex !== -1) {
        const date = new Date();
        date.setHours(0, 0, 0, 0); 
        while (date.getDay() !== dayIndex) {
            date.setDate(date.getDate() - 1);
        }
        return toYyyyMmDd(date);
    }

    try {
        const date = new Date(`${dateStr} ${year}`);
        if (!isNaN(date.getTime())) {
            return toYyyyMmDd(date);
        }
    } catch (e) { /* Ignore parsing errors */ }
    
    return dateStr; // Fallback to the original string if parsing fails
}

/**
 * Converts LinkedIn time format (e.g., "8:48 PM", "10:08 AM") to 24-hour format (e.g., "20:48", "10:08")
 * @param timeStr The time string from LinkedIn UI (e.g., "3:26 PM", "11:12 AM")
 * @returns A formatted "HH:MM" string in 24-hour format
 */
export function convertTo24HourFormat(timeStr: string): string {
    if (!timeStr || timeStr === 'Unknown') {
        return timeStr;
    }

    // Check if it's already in 24-hour format (no AM/PM)
    if (!timeStr.includes('AM') && !timeStr.includes('PM')) {
        return timeStr;
    }

    try {
        // Parse the time string
        const timeMatch = timeStr.match(/^(\d{1,2}):(\d{2})\s*(AM|PM)$/i);
        if (!timeMatch) {
            console.warn(`Unable to parse time format: "${timeStr}"`);
            return timeStr; // Return original if we can't parse
        }

        let hour = parseInt(timeMatch[1], 10);
        const minute = timeMatch[2];
        const period = timeMatch[3].toUpperCase();

        // Convert to 24-hour format
        if (period === 'AM') {
            if (hour === 12) {
                hour = 0; // 12:XX AM becomes 00:XX
            }
        } else if (period === 'PM') {
            if (hour !== 12) {
                hour += 12; // Add 12 for PM times except 12:XX PM
            }
        }

        // Format with leading zero if needed
        const formattedHour = hour.toString().padStart(2, '0');
        return `${formattedHour}:${minute}`;
    } catch (error) {
        console.warn(`Error converting time format "${timeStr}":`, error);
        return timeStr; // Return original on error
    }
}

/**
 * Generates a unique and deterministic 32-character ID from message details.
 * @param sender The message sender's name.
 * @param date The formatted message date (YYYY-MM-DD).
 * @param time The message time.
 * @param snippet The message content.
 * @returns A promise that resolves to a 32-character hex string ID.
 */
export async function generateId(sender: string, date: string, time: string, snippet: string): Promise<string> {
    const data = `${sender}-${date}-${time}-${snippet}`;
    const encoder = new TextEncoder();
    const dataBuffer = encoder.encode(data);
    const hashBuffer = await crypto.subtle.digest('SHA-256', dataBuffer);
    const hashArray = Array.from(new Uint8Array(hashBuffer));
    const hashHex = hashArray.map(b => b.toString(16).padStart(2, '0')).join('');
    return hashHex.slice(0, 32); // Return a 32-character ID
} 
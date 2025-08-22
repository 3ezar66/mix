import axios from 'axios';
export async function lookupLocation(ip) {
    try {
        const response = await axios.get(`https://ipapi.co/${ip}/json/`);
        return {
            city: response.data.city || null,
            country: response.data.country_name || null,
            latitude: response.data.latitude || null,
            longitude: response.data.longitude || null
        };
    }
    catch (error) {
        console.error('GeoIP lookup failed:', error);
        return {
            city: null,
            country: null,
            latitude: null,
            longitude: null
        };
    }
}

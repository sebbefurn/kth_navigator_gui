import axios from 'axios';

const getCSRFToken = async () => {
  try {
    const response = await axios.get('http://localhost:8000/api/csrf-cookie/');
    return response.data.csrfToken;
  } catch (error) {
    console.error('Failed to retrieve CSRF token:', error);
    return null;
  }
};

export default getCSRFToken;

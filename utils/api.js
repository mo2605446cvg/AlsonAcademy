import axios from 'axios';
import PushNotification from 'react-native-push-notification';

const API_URL = 'https://ki74.alalsunacademy.com/api';

const handleError = (error, endpoint) => {
  console.error(`Error in ${endpoint}:`, {
    message: error.message,
    response: error.response?.data,
    status: error.response?.status,
    headers: error.response?.headers,
  });
  throw new Error(error.response?.data?.error || `Failed to ${endpoint}`);
};

// Initialize push notifications
PushNotification.configure({
  onNotification: function (notification) {
    console.log('NOTIFICATION:', notification);
  },
  onRegister: function (token) {
    console.log('TOKEN:', token);
  },
  permissions: {
    alert: true,
    badge: true,
    sound: true,
  },
  popInitialNotification: true,
  requestPermissions: true,
});

PushNotification.createChannel(
  {
    channelId: 'alson-academy-channel',
    channelName: 'Alson Academy Notifications',
    channelDescription: 'Default channel for notifications',
    soundName: 'default',
    importance: 4,
    vibrate: true,
  },
  (created) => console.log(`createChannel returned '${created}'`)
);

const scheduleNotification = (title, body) => {
  PushNotification.localNotification({
    channelId: 'alson-academy-channel',
    title: title,
    message: body,
  });
};

export const loginUser = async (code, password) => {
  try {
    console.log('API request payload:', { code, password });
    const response = await axios.post(`${API_URL}/api.php?table=users&action=login`, { code, password });
    return response.data;
  } catch (error) {
    handleError(error, 'loginUser');
  }
};

export const getUsers = async () => {
  try {
    const response = await axios.get(`${API_URL}/api.php?table=users&action=all`);
    return response.data;
  } catch (error) {
    handleError(error, 'getUsers');
  }
};

export const addUser = async (userData) => {
  try {
    const response = await axios.post(`${API_URL}/api.php?table=users`, userData);
    return response.data;
  } catch (error) {
    handleError(error, 'addUser');
  }
};

export const deleteUser = async (code) => {
  try {
    const response = await axios.delete(`${API_URL}/api.php?table=users&code=${code}`);
    return response.data;
  } catch (error) {
    handleError(error, 'deleteUser');
  }
};

export const getContent = async (department, division) => {
  try {
    const response = await axios.get(`${API_URL}/api.php?table=content&action=all&department=${department}&division=${division}`);
    return response.data;
  } catch (error) {
    handleError(error, 'getContent');
  }
};

export const uploadContent = async (title, file, uploaded_by, department, division) => {
  try {
    const formData = new FormData();
    formData.append('file', {
      uri: file.uri,
      name: file.name,
      type: file.type,
    });
    const response = await axios.post(`${API_URL}/upload.php`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    const file_path = response.data.file_path;
    const file_type = file.type.split('/')[1];
    const upload_date = new Date().toISOString();
    const id = Date.now().toString();
    await axios.post(`${API_URL}/api.php?table=content`, {
      id,
      title,
      file_path,
      file_type,
      uploaded_by,
      upload_date,
      department,
      division,
    });
    scheduleNotification('محتوى جديد', `تم رفع محتوى جديد: ${title}`);
    return response.data;
  } catch (error) {
    handleError(error, 'uploadContent');
  }
};

export const deleteContent = async (id) => {
  try {
    const response = await axios.delete(`${API_URL}/api.php?table=content&id=${id}`);
    return response.data;
  } catch (error) {
    handleError(error, 'deleteContent');
  }
};

export const getChatMessages = async (department, division) => {
  try {
    const response = await axios.get(`${API_URL}/api.php?table=messages&department=${department}&division=${division}`);
    return response.data;
  } catch (error) {
    handleError(error, 'getChatMessages');
  }
};

export const sendMessage = async (sender_id, department, division, content) => {
  try {
    const id = Date.now().toString();
    const timestamp = new Date().toISOString();
    const response = await axios.post(`${API_URL}/api.php?table=messages`, {
      id,
      content,
      sender_id,
      department,
      division,
      timestamp,
    });
    scheduleNotification('رسالة جديدة', `رسالة جديدة في الشات: ${content.substring(0, 50)}...`);
    return response.data;
  } catch (error) {
    handleError(error, 'sendMessage');
  }
};

export const getResults = async (studentId) => {
  try {
    const response = await axios.get(`${API_URL}/api.php?table=results&studentId=${studentId}`);
    return response.data;
  } catch (error) {
    handleError(error, 'getResults');
  }
};
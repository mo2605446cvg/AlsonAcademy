import React, { useState, useEffect, useContext } from 'react';
import { View, Text, TextInput, TouchableOpacity, FlatList, Alert } from 'react-native';
import { t } from 'react-native-tailwindcss';
import Icon from 'react-native-vector-icons/MaterialIcons';
import AppBar from '../components/AppBar';
import { PRIMARY_COLOR, TEXT_COLOR } from '../utils/colors';
import { UserContext } from '../context/UserContext';
import { getChatMessages, sendMessage } from '../utils/api';

const Chat = ({ navigation }) => {
  const { user, logout } = useContext(UserContext);
  const [messages, setMessages] = useState([]);
  const [newMessage, setNewMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    fetchMessages();
  }, []);

  const fetchMessages = async () => {
    setIsLoading(true);
    try {
      const data = await getChatMessages(user.department, user.division);
      setMessages(data);
    } catch (error) {
      Alert.alert('خطأ', 'فشل في جلب الرسائل');
    } finally {
      setIsLoading(false);
    }
  };

  const handleSendMessage = async () => {
    if (!newMessage.trim()) {
      Alert.alert('خطأ', 'يرجى إدخال نص الرسالة');
      return;
    }
    setIsLoading(true);
    try {
      await sendMessage(user.code, user.department, user.division, newMessage);
      setNewMessage('');
      fetchMessages();
    } catch (error) {
      Alert.alert('خطأ', 'فشل في إرسال الرسالة');
    } finally {
      setIsLoading(false);
    }
  };

  const renderMessage = ({ item }) => (
    <View style={[t.bgWhite, t.rounded2xl, t.p4, t.mB2, { elevation: 5 }]}>
      <Text style={[t.textBase, t.fontBold, { color: TEXT_COLOR }]}>{item.username}</Text>
      <Text style={[t.textSm, { color: TEXT_COLOR }]}>{item.content}</Text>
      <Text style={[t.textXs, t.textGray500, t.mT1]}>{new Date(item.timestamp).toLocaleString('ar-EG')}</Text>
    </View>
  );

  return (
    <View style={[t.flex1, t.bgGray200]}>
      <AppBar navigation={navigation} isAdmin={user.role === 'admin'} handleLogout={() => { logout(); navigation.navigate('Login'); }} />
      <View style={[t.flex1, t.p4]}>
        <Text style={[t.text3xl, t.fontBold, t.textBlue800, t.mB4, t.textCenter]}>الشات</Text>
        <FlatList
          data={messages}
          renderItem={renderMessage}
          keyExtractor={(item) => item.id}
          ListEmptyComponent={<Text style={[t.textBase, t.textCenter, { color: TEXT_COLOR }]}>لا توجد رسائل</Text>}
          refreshing={isLoading}
          onRefresh={fetchMessages}
        />
        {user.role === 'admin' && (
          <View style={[t.flexRow, t.mT2, t.itemsCenter]}>
            <TextInput
              style={[t.flex1, t.border, t.borderGray400, t.rounded, t.p2, t.mR2, { color: TEXT_COLOR }]}
              placeholder="اكتب رسالتك..."
              value={newMessage}
              onChangeText={setNewMessage}
              editable={!isLoading}
            />
            <TouchableOpacity
              style={[t.bgBlue800, t.roundedXl, t.p3, isLoading ? t.opacity50 : t.opacity100]}
              onPress={handleSendMessage}
              disabled={isLoading}
            >
              <Icon name="send" size={24} color="#FFFFFF" />
            </TouchableOpacity>
          </View>
        )}
      </View>
    </View>
  );
};

export default Chat;
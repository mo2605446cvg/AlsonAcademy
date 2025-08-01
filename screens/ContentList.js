import React, { useState, useEffect, useContext } from 'react';
import { View, Text, FlatList, TouchableOpacity, Alert, Linking } from 'react-native';
import { t } from 'react-native-tailwindcss';
import Icon from 'react-native-vector-icons/MaterialIcons';
import AppBar from '../components/AppBar';
import { PRIMARY_COLOR, TEXT_COLOR } from '../utils/colors';
import { UserContext } from '../context/UserContext';
import { getContent, deleteContent } from '../utils/api';

const ContentList = ({ navigation }) => {
  const { user, logout } = useContext(UserContext);
  const [content, setContent] = useState([]);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    fetchContent();
  }, []);

  const fetchContent = async () => {
    setIsLoading(true);
    try {
      const data = await getContent(user.department, user.division);
      setContent(data);
    } catch (error) {
      Alert.alert('خطأ', 'فشل في جلب المحتوى');
    } finally {
      setIsLoading(false);
    }
  };

  const handleDeleteContent = async (id) => {
    Alert.alert(
      'تأكيد الحذف',
      'هل أنت متأكد من حذف هذا المحتوى؟',
      [
        { text: 'إلغاء', style: 'cancel' },
        {
          text: 'حذف',
          style: 'destructive',
          onPress: async () => {
            setIsLoading(true);
            try {
              await deleteContent(id);
              fetchContent();
              Alert.alert('نجاح', 'تم حذف المحتوى بنجاح');
            } catch (error) {
              Alert.alert('خطأ', 'فشل في حذف المحتوى');
            } finally {
              setIsLoading(false);
            }
          },
        },
      ]
    );
  };

  const handleOpenContent = async (file_path) => {
    try {
      await Linking.openURL(`https://ki74.alalsunacademy.com/api/${file_path}`);
    } catch (error) {
      Alert.alert('خطأ', 'فشل في فتح الملف');
    }
  };

  const renderContent = ({ item }) => (
    <View style={[t.bgWhite, t.rounded2xl, t.p4, t.mB2, t.flexRow, t.itemsCenter, t.justifyBetween, { elevation: 5 }]}>
      <TouchableOpacity onPress={() => handleOpenContent(item.file_path)} style={[t.flex1]}>
        <Text style={[t.textBase, t.fontBold, { color: TEXT_COLOR }]}>{item.title}</Text>
        <Text style={[t.textSm, { color: TEXT_COLOR }]}>النوع: {item.file_type}</Text>
        <Text style={[t.textSm, { color: TEXT_COLOR }]}>تاريخ الرفع: {new Date(item.upload_date).toLocaleDateString('ar-EG')}</Text>
        <Text style={[t.textSm, { color: TEXT_COLOR }]}>بواسطة: {item.uploaded_by}</Text>
      </TouchableOpacity>
      {user.role === 'admin' && (
        <TouchableOpacity onPress={() => handleDeleteContent(item.id)}>
          <Icon name="delete" size={24} color="#EF5350" />
        </TouchableOpacity>
      )}
    </View>
  );

  return (
    <View style={[t.flex1, t.bgGray200]}>
      <AppBar navigation={navigation} isAdmin={user.role === 'admin'} handleLogout={() => { logout(); navigation.navigate('Login'); }} />
      <View style={[t.flex1, t.p4]}>
        <Text style={[t.text3xl, t.fontBold, t.textBlue800, t.mB4, t.textCenter]}>المحتوى</Text>
        <FlatList
          data={content}
          renderItem={renderContent}
          keyExtractor={(item) => item.id}
          ListEmptyComponent={<Text style={[t.textBase, t.textCenter, { color: TEXT_COLOR }]}>لا يوجد محتوى</Text>}
          refreshing={isLoading}
          onRefresh={fetchContent}
        />
        <TouchableOpacity
          style={[t.bgBlue800, t.roundedXl, t.p3, t.w48, t.itemsCenter, t.mT4]}
          onPress={() => navigation.navigate('ContentUpload')}
        >
          <Text style={[t.textWhite, t.textBase]}>رفع محتوى جديد</Text>
        </TouchableOpacity>
      </View>
    </View>
  );
};

export default ContentList;
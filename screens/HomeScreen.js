import React, { useContext } from 'react';
import { View, Text, TouchableOpacity } from 'react-native';
import { t } from 'react-native-tailwindcss';
import AppBar from '../components/AppBar';
import { UserContext } from '../context/UserContext';
import { PRIMARY_COLOR, TEXT_COLOR } from '../utils/colors';

const HomeScreen = ({ navigation }) => {
  const { user, logout } = useContext(UserContext);

  return (
    <View style={[t.flex1, t.bgGray200]}>
      <AppBar navigation={navigation} isAdmin={user.role === 'admin'} handleLogout={() => { logout(); navigation.navigate('Login'); }} />
      <View style={[t.flex1, t.p4, t.itemsCenter, t.justifyCenter]}>
        <Text style={[t.text3xl, t.fontBold, t.textBlue800, t.mB4]}>مرحبًا، {user.username}!</Text>
        <TouchableOpacity
          style={[t.bgBlue800, t.roundedXl, t.p3, t.w48, t.itemsCenter, t.mB2]}
          onPress={() => navigation.navigate('Content')}
        >
          <Text style={[t.textWhite, t.textBase]}>عرض المحتوى</Text>
        </TouchableOpacity>
        {user.role === 'admin' && (
          <TouchableOpacity
            style={[t.bgBlue800, t.roundedXl, t.p3, t.w48, t.itemsCenter, t.mB2]}
            onPress={() => navigation.navigate('UserManagement')}
          >
            <Text style={[t.textWhite, t.textBase]}>لوحة التحكم</Text>
          </TouchableOpacity>
        )}
        <TouchableOpacity
          style={[t.bgBlue800, t.roundedXl, t.p3, t.w48, t.itemsCenter, t.mB2]}
          onPress={() => navigation.navigate('Chat')}
        >
          <Text style={[t.textWhite, t.textBase]}>الشات</Text>
        </TouchableOpacity>
        <TouchableOpacity
          style={[t.bgBlue800, t.roundedXl, t.p3, t.w48, t.itemsCenter, t.mB2]}
          onPress={() => navigation.navigate('Results')}
        >
          <Text style={[t.textWhite, t.textBase]}>النتائج</Text>
        </TouchableOpacity>
        <TouchableOpacity
          style={[t.bgBlue800, t.roundedXl, t.p3, t.w48, t.itemsCenter]}
          onPress={() => navigation.navigate('Profile')}
        >
          <Text style={[t.textWhite, t.textBase]}>الملف الشخصي</Text>
        </TouchableOpacity>
      </View>
    </View>
  );
};

export default HomeScreen;
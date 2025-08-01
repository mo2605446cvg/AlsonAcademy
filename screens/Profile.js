import React, { useContext } from 'react';
import { View, Text, TouchableOpacity } from 'react-native';
import { t } from 'react-native-tailwindcss';
import AppBar from '../components/AppBar';
import { PRIMARY_COLOR, TEXT_COLOR } from '../utils/colors';
import { UserContext } from '../context/UserContext';

const Profile = ({ navigation }) => {
  const { user, logout } = useContext(UserContext);

  return (
    <View style={[t.flex1, t.bgGray200]}>
      <AppBar navigation={navigation} isAdmin={user.role === 'admin'} handleLogout={() => { logout(); navigation.navigate('Login'); }} />
      <View style={[t.flex1, t.p4, t.itemsCenter]}>
        <Text style={[t.text3xl, t.fontBold, t.textBlue800, t.mB4]}>الملف الشخصي</Text>
        <View style={[t.wFull, t.maxW96, t.bgWhite, t.rounded2xl, t.p4, { elevation: 5 }]}>
          <Text style={[t.textLg, t.fontBold, t.mB2, { color: TEXT_COLOR }]}>اسم المستخدم: {user.username}</Text>
          <Text style={[t.textLg, t.mB2, { color: TEXT_COLOR }]}>كود المستخدم: {user.code}</Text>
          <Text style={[t.textLg, t.mB2, { color: TEXT_COLOR }]}>القسم: {user.department}</Text>
          <Text style={[t.textLg, t.mB2, { color: TEXT_COLOR }]}>الشعبة: {user.division}</Text>
          <Text style={[t.textLg, t.mB2, { color: TEXT_COLOR }]}>الدور: {user.role}</Text>
        </View>
        <TouchableOpacity
          style={[t.bgBlue800, t.roundedXl, t.p3, t.w48, t.itemsCenter, t.mT4]}
          onPress={() => navigation.navigate('Home')}
        >
          <Text style={[t.textWhite, t.textBase]}>عودة</Text>
        </TouchableOpacity>
      </View>
    </View>
  );
};

export default Profile;
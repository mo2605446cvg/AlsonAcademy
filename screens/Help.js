import React, { useContext } from 'react';
import { View, Text, TouchableOpacity } from 'react-native';
import { t } from 'react-native-tailwindcss';
import AppBar from '../components/AppBar';
import { PRIMARY_COLOR, TEXT_COLOR } from '../utils/colors';
import { UserContext } from '../context/UserContext';

const Help = ({ navigation }) => {
  const { user, logout } = useContext(UserContext);

  return (
    <View style={[t.flex1, t.bgGray200]}>
      <AppBar navigation={navigation} isAdmin={user.role === 'admin'} handleLogout={() => { logout(); navigation.navigate('Login'); }} />
      <View style={[t.flex1, t.p4, t.itemsCenter]}>
        <Text style={[t.text3xl, t.fontBold, t.textBlue800, t.mB4]}>المساعدة</Text>
        <View style={[t.wFull, t.maxW96, t.bgWhite, t.rounded2xl, t.p4, { elevation: 5 }]}>
          <Text style={[t.textLg, t.fontBold, t.mB2, { color: TEXT_COLOR }]}>كيفية استخدام التطبيق</Text>
          <Text style={[t.textBase, t.mB2, { color: TEXT_COLOR }]}>1. تسجيل الدخول باستخدام كود المستخدم وكلمة المرور.</Text>
          <Text style={[t.textBase, t.mB2, { color: TEXT_COLOR }]}>2. عرض المحتوى التعليمي حسب القسم والشعبة.</Text>
          <Text style={[t.textBase, t.mB2, { color: TEXT_COLOR }]}>3. التواصل عبر الشات (للأدمن فقط).</Text>
          <Text style={[t.textBase, t.mB2, { color: TEXT_COLOR }]}>4. التحقق من النتائج في صفحة النتائج.</Text>
          <Text style={[t.textBase, t.mB2, { color: TEXT_COLOR }]}>للدعم، تواصل مع إدارة الألسن أكاديمي.</Text>
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

export default Help;
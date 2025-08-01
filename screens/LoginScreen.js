import React, { useState, useContext } from 'react';
import { View, Text, TextInput, TouchableOpacity, Image, Alert } from 'react-native';
import { t } from 'react-native-tailwindcss';
import Icon from 'react-native-vector-icons/MaterialIcons';
import { PRIMARY_COLOR, TEXT_COLOR } from '../utils/colors';
import { loginUser } from '../utils/api';
import { UserContext } from '../context/UserContext';

const LoginScreen = ({ navigation }) => {
  const { login } = useContext(UserContext);
  const [code, setCode] = useState('');
  const [password, setPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const validateLogin = async () => {
    if (!code.trim() || !password.trim()) {
      Alert.alert('خطأ', 'يرجى إدخال كود المستخدم وكلمة المرور');
      return;
    }
    setIsLoading(true);
    try {
      console.log('Sending login request:', { code, password });
      const user = await loginUser(code, password);
      if (user && user.code) {
        console.log('Login successful:', user);
        login(user);
        navigation.navigate('Home');
      } else {
        throw new Error(user?.error || 'كود المستخدم أو كلمة المرور غير صحيحة');
      }
    } catch (error) {
      console.error('Login error:', error.message);
      Alert.alert('خطأ', error.message || 'كود المستخدم أو كلمة المرور غير صحيحة');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <View style={[t.flex1, t.bgGray200, t.itemsCenter, t.justifyCenter, t.p4]}>
      <Image source={require('../assets/icon.png')} style={[t.w32, t.h32]} />
      <Text style={[t.text3xl, t.fontBold, t.textBlue800, t.mB4]}>مرحبًا بك في الألسن!</Text>
      <View style={[t.wFull, t.maxW96, t.bgWhite, t.rounded2xl, t.border, t.borderBlue800, t.mB4, t.flexRow, t.itemsCenter]}>
        <Icon name="person" size={24} color={PRIMARY_COLOR} style={[t.mL2]} />
        <TextInput
          style={[t.flex1, t.p2, t.textBase, { color: TEXT_COLOR }]}
          placeholder="كود المستخدم (مثال: ADMIN001)"
          value={code}
          onChangeText={setCode}
          editable={!isLoading}
        />
      </View>
      <View style={[t.wFull, t.maxW96, t.bgWhite, t.rounded2xl, t.border, t.borderBlue800, t.mB4, t.flexRow, t.itemsCenter]}>
        <Icon name="lock" size={24} color={PRIMARY_COLOR} style={[t.mL2]} />
        <TextInput
          style={[t.flex1, t.p2, t.textBase, { color: TEXT_COLOR }]}
          placeholder="كلمة المرور"
          secureTextEntry
          value={password}
          onChangeText={setPassword}
          editable={!isLoading}
        />
      </View>
      <TouchableOpacity
        style={[t.bgBlue800, t.roundedXl, t.p3, t.w48, t.itemsCenter, t.mB4, isLoading ? t.opacity50 : t.opacity100]}
        onPress={validateLogin}
        disabled={isLoading}
      >
        <Text style={[t.textWhite, t.textBase, t.fontBold]}>{isLoading ? 'جارٍ التحميل...' : 'تسجيل الدخول'}</Text>
      </TouchableOpacity>
      <TouchableOpacity disabled={isLoading}>
        <Text style={[t.textBlue800, t.textBase]}>هل نسيت كلمة المرور؟</Text>
      </TouchableOpacity>
    </View>
  );
};

export default LoginScreen;
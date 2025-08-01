import React, { useState, useContext } from 'react';
import { View, Text, TextInput, TouchableOpacity, Alert } from 'react-native';
import DocumentPicker from 'react-native-document-picker';
import { t } from 'react-native-tailwindcss';
import { Picker } from '@react-native-picker/picker';
import Icon from 'react-native-vector-icons/MaterialIcons';
import AppBar from '../components/AppBar';
import { PRIMARY_COLOR, TEXT_COLOR } from '../utils/colors';
import { UserContext } from '../context/UserContext';
import { uploadContent } from '../utils/api';

const ContentUpload = ({ navigation }) => {
  const { user, logout } = useContext(UserContext);
  const [title, setTitle] = useState('');
  const [file, setFile] = useState(null);
  const [department, setDepartment] = useState(user.department);
  const [division, setDivision] = useState(user.division);
  const [isLoading, setIsLoading] = useState(false);

  const departments = ['Math', 'Science', 'Computer', 'Physics', 'Chemistry'];
  const divisions = ['Division A', 'Division B'];

  const pickDocument = async () => {
    try {
      const result = await DocumentPicker.pick({
        type: [DocumentPicker.types.pdf, DocumentPicker.types.plainText],
      });
      setFile({
        uri: result[0].uri,
        name: result[0].name,
        type: result[0].type,
      });
    } catch (error) {
      if (!DocumentPicker.isCancel(error)) {
        Alert.alert('خطأ', 'فشل في اختيار الملف');
      }
    }
  };

  const handleUpload = async () => {
    if (!title.trim() || !file) {
      Alert.alert('خطأ', 'يرجى إدخال العنوان واختيار ملف');
      return;
    }
    setIsLoading(true);
    try {
      await uploadContent(title, file, user.code, department, division);
      setTitle('');
      setFile(null);
      Alert.alert('نجاح', 'تم رفع المحتوى بنجاح');
    } catch (error) {
      Alert.alert('خطأ', 'فشل في رفع المحتوى');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <View style={[t.flex1, t.bgGray200]}>
      <AppBar navigation={navigation} isAdmin={user.role === 'admin'} handleLogout={() => { logout(); navigation.navigate('Login'); }} />
      <View style={[t.flex1, t.p4, t.itemsCenter]}>
        <Text style={[t.text3xl, t.fontBold, t.textBlue800, t.mB4]}>رفع المحتوى</Text>
        <View style={[t.wFull, t.maxW96, t.bgWhite, t.rounded2xl, t.p4, { elevation: 5 }]}>
          <TextInput
            style={[t.border, t.borderGray400, t.rounded, t.p2, t.mB2, { color: TEXT_COLOR }]}
            placeholder="عنوان المحتوى"
            value={title}
            onChangeText={setTitle}
          />
          <Picker
            selectedValue={department}
            onValueChange={setDepartment}
            style={[t.border, t.borderGray400, t.rounded, t.mB2]}
            enabled={user.role === 'admin'}
          >
            {departments.map((dept) => (
              <Picker.Item key={dept} label={dept} value={dept} />
            ))}
          </Picker>
          <Picker
            selectedValue={division}
            onValueChange={setDivision}
            style={[t.border, t.borderGray400, t.rounded, t.mB2]}
            enabled={user.role === 'admin'}
          >
            {divisions.map((div) => (
              <Picker.Item key={div} label={div} value={div} />
            ))}
          </Picker>
          <TouchableOpacity
            style={[t.bgBlue800, t.roundedXl, t.p3, t.mB2, t.itemsCenter]}
            onPress={pickDocument}
          >
            <Text style={[t.textWhite, t.textBase]}>اختيار ملف</Text>
          </TouchableOpacity>
          {file && <Text style={[t.textSm, t.mB2, { color: TEXT_COLOR }]}>تم اختيار: {file.name}</Text>}
          <TouchableOpacity
            style={[t.bgBlue800, t.roundedXl, t.p3, t.itemsCenter, isLoading ? t.opacity50 : t.opacity100]}
            onPress={handleUpload}
            disabled={isLoading}
          >
            <Text style={[t.textWhite, t.textBase]}>{isLoading ? 'جارٍ الرفع...' : 'رفع المحتوى'}</Text>
          </TouchableOpacity>
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

export default ContentUpload;
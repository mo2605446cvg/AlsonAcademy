import React, { useState, useEffect, useContext } from 'react';
import { View, Text, TextInput, TouchableOpacity, FlatList, Alert } from 'react-native';
import { t } from 'react-native-tailwindcss';
import Icon from 'react-native-vector-icons/MaterialIcons';
import { Picker } from '@react-native-picker/picker';
import AppBar from '../components/AppBar';
import { PRIMARY_COLOR, TEXT_COLOR } from '../utils/colors';
import { UserContext } from '../context/UserContext';
import { getUsers, addUser, deleteUser } from '../utils/api';

const UserManagement = ({ navigation }) => {
  const { user, logout } = useContext(UserContext);
  const [users, setUsers] = useState([]);
  const [newUser, setNewUser] = useState({
    code: '',
    username: '',
    department: 'Math',
    division: 'Division A',
    role: 'user',
    password: '',
  });
  const [isLoading, setIsLoading] = useState(false);

  const departments = ['Math', 'Science', 'Computer', 'Physics', 'Chemistry'];
  const divisions = ['Division A', 'Division B'];
  const roles = ['admin', 'user'];

  useEffect(() => {
    fetchUsers();
  }, []);

  const fetchUsers = async () => {
    setIsLoading(true);
    try {
      const data = await getUsers();
      setUsers(data);
    } catch (error) {
      Alert.alert('خطأ', 'فشل في جلب المستخدمين');
    } finally {
      setIsLoading(false);
    }
  };

  const handleAddUser = async () => {
    if (!newUser.code || !newUser.username || !newUser.password) {
      Alert.alert('خطأ', 'يرجى ملء جميع الحقول');
      return;
    }
    setIsLoading(true);
    try {
      await addUser(newUser);
      setNewUser({ code: '', username: '', department: 'Math', division: 'Division A', role: 'user', password: '' });
      fetchUsers();
      Alert.alert('نجاح', 'تم إضافة المستخدم بنجاح');
    } catch (error) {
      Alert.alert('خطأ', 'فشل في إضافة المستخدم');
    } finally {
      setIsLoading(false);
    }
  };

  const handleDeleteUser = async (code) => {
    Alert.alert(
      'تأكيد الحذف',
      'هل أنت متأكد من حذف هذا المستخدم؟',
      [
        { text: 'إلغاء', style: 'cancel' },
        {
          text: 'حذف',
          style: 'destructive',
          onPress: async () => {
            setIsLoading(true);
            try {
              await deleteUser(code);
              fetchUsers();
              Alert.alert('نجاح', 'تم حذف المستخدم بنجاح');
            } catch (error) {
              Alert.alert('خطأ', 'فشل في حذف المستخدم');
            } finally {
              setIsLoading(false);
            }
          },
        },
      ]
    );
  };

  const renderUser = ({ item }) => (
    <View style={[t.bgWhite, t.rounded2xl, t.p4, t.mB2, t.flexRow, t.itemsCenter, t.justifyBetween, { elevation: 5 }]}>
      <View>
        <Text style={[t.textBase, t.fontBold, { color: TEXT_COLOR }]}>{item.username}</Text>
        <Text style={[t.textSm, { color: TEXT_COLOR }]}>كود: {item.code}</Text>
        <Text style={[t.textSm, { color: TEXT_COLOR }]}>القسم: {item.department}</Text>
        <Text style={[t.textSm, { color: TEXT_COLOR }]}>الشعبة: {item.division}</Text>
        <Text style={[t.textSm, { color: TEXT_COLOR }]}>الدور: {item.role}</Text>
      </View>
      <TouchableOpacity onPress={() => handleDeleteUser(item.code)}>
        <Icon name="delete" size={24} color="#EF5350" />
      </TouchableOpacity>
    </View>
  );

  return (
    <View style={[t.flex1, t.bgGray200]}>
      <AppBar navigation={navigation} isAdmin={true} handleLogout={() => { logout(); navigation.navigate('Login'); }} />
      <View style={[t.flex1, t.p4]}>
        <Text style={[t.text3xl, t.fontBold, t.textBlue800, t.mB4, t.textCenter]}>لوحة التحكم</Text>
        <View style={[t.bgWhite, t.rounded2xl, t.p4, t.mB4, { elevation: 5 }]}>
          <Text style={[t.textLg, t.fontBold, t.mB2, { color: TEXT_COLOR }]}>إضافة مستخدم جديد</Text>
          <View style={[t.mB2]}>
            <TextInput
              style={[t.border, t.borderGray400, t.rounded, t.p2, t.mB2, { color: TEXT_COLOR }]}
              placeholder="كود المستخدم"
              value={newUser.code}
              onChangeText={(text) => setNewUser({ ...newUser, code: text })}
            />
            <TextInput
              style={[t.border, t.borderGray400, t.rounded, t.p2, t.mB2, { color: TEXT_COLOR }]}
              placeholder="اسم المستخدم"
              value={newUser.username}
              onChangeText={(text) => setNewUser({ ...newUser, username: text })}
            />
            <Picker
              selectedValue={newUser.department}
              onValueChange={(value) => setNewUser({ ...newUser, department: value })}
              style={[t.border, t.borderGray400, t.rounded, t.mB2]}
            >
              {departments.map((dept) => (
                <Picker.Item key={dept} label={dept} value={dept} />
              ))}
            </Picker>
            <Picker
              selectedValue={newUser.division}
              onValueChange={(value) => setNewUser({ ...newUser, division: value })}
              style={[t.border, t.borderGray400, t.rounded, t.mB2]}
            >
              {divisions.map((div) => (
                <Picker.Item key={div} label={div} value={div} />
              ))}
            </Picker>
            <Picker
              selectedValue={newUser.role}
              onValueChange={(value) => setNewUser({ ...newUser, role: value })}
              style={[t.border, t.borderGray400, t.rounded, t.mB2]}
            >
              {roles.map((role) => (
                <Picker.Item key={role} label={role} value={role} />
              ))}
            </Picker>
            <TextInput
              style={[t.border, t.borderGray400, t.rounded, t.p2, t.mB2, { color: TEXT_COLOR }]}
              placeholder="كلمة المرور"
              secureTextEntry
              value={newUser.password}
              onChangeText={(text) => setNewUser({ ...newUser, password: text })}
            />
          </View>
          <TouchableOpacity
            style={[t.bgBlue800, t.roundedXl, t.p3, t.itemsCenter, isLoading ? t.opacity50 : t.opacity100]}
            onPress={handleAddUser}
            disabled={isLoading}
          >
            <Text style={[t.textWhite, t.textBase]}>إضافة المستخدم</Text>
          </TouchableOpacity>
        </View>
        <Text style={[t.textLg, t.fontBold, t.mB2, { color: TEXT_COLOR }]}>قائمة المستخدمين</Text>
        <FlatList
          data={users}
          renderItem={renderUser}
          keyExtractor={(item) => item.code}
          ListEmptyComponent={<Text style={[t.textBase, t.textCenter, { color: TEXT_COLOR }]}>لا يوجد مستخدمين</Text>}
        />
      </View>
    </View>
  );
};

export default UserManagement;
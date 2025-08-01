import React, { useState, useEffect, useContext } from 'react';
import { View, Text, Alert } from 'react-native';
import { t } from 'react-native-tailwindcss';
import AppBar from '../components/AppBar';
import { PRIMARY_COLOR, TEXT_COLOR } from '../utils/colors';
import { UserContext } from '../context/UserContext';
import { getResults } from '../utils/api';

const Results = ({ navigation }) => {
  const { user, logout } = useContext(UserContext);
  const [results, setResults] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    fetchResults();
  }, []);

  const fetchResults = async () => {
    setIsLoading(true);
    try {
      const data = await getResults(user.code);
      setResults(data);
    } catch (error) {
      Alert.alert('خطأ', 'فشل في جلب النتائج');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <View style={[t.flex1, t.bgGray200]}>
      <AppBar navigation={navigation} isAdmin={user.role === 'admin'} handleLogout={() => { logout(); navigation.navigate('Login'); }} />
      <View style={[t.flex1, t.p4, t.itemsCenter]}>
        <Text style={[t.text3xl, t.fontBold, t.textBlue800, t.mB4]}>النتائج</Text>
        {isLoading ? (
          <Text style={[t.textBase, { color: TEXT_COLOR }]}>جارٍ التحميل...</Text>
        ) : results ? (
          <View style={[t.wFull, t.maxW96, t.bgWhite, t.rounded2xl, t.p4, { elevation: 5 }]}>
            <Text style={[t.textLg, t.fontBold, t.mB2, { color: TEXT_COLOR }]}>الدرجة: {results.score}</Text>
            <Text style={[t.textLg, t.mB2, { color: TEXT_COLOR }]}>المادة: {results.subject}</Text>
            <Text style={[t.textLg, t.mB2, { color: TEXT_COLOR }]}>التاريخ: {new Date(results.date).toLocaleDateString('ar-EG')}</Text>
          </View>
        ) : (
          <Text style={[t.textBase, t.textCenter, { color: TEXT_COLOR }]}>لا توجد نتائج</Text>
        )}
      </View>
    </View>
  );
};

export default Results;
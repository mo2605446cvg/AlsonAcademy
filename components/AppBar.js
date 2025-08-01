import React from 'react';
import { View, Text, TouchableOpacity } from 'react-native';
import { t } from 'react-native-tailwindcss';
import Icon from 'react-native-vector-icons/MaterialIcons';
import { PRIMARY_COLOR, TEXT_COLOR } from '../utils/colors';

const AppBar = ({ navigation, isAdmin, handleLogout }) => {
  return (
    <View style={[t.bgBlue800, t.p4, t.flexRow, t.itemsCenter, t.justifyBetween]}>
      <TouchableOpacity onPress={() => navigation.navigate('Home')}>
        <Icon name="home" size={24} color="#FFFFFF" />
      </TouchableOpacity>
      <Text style={[t.textWhite, t.textLg, t.fontBold]}>الألسن أكاديمي</Text>
      <View style={[t.flexRow]}>
        {isAdmin && (
          <TouchableOpacity onPress={() => navigation.navigate('UserManagement')} style={[t.mR2]}>
            <Icon name="admin-panel-settings" size={24} color="#FFFFFF" />
          </TouchableOpacity>
        )}
        <TouchableOpacity onPress={() => navigation.navigate('ContentUpload')} style={[t.mR2]}>
          <Icon name="upload" size={24} color="#FFFFFF" />
        </TouchableOpacity>
        <TouchableOpacity onPress={() => navigation.navigate('Help')} style={[t.mR2]}>
          <Icon name="help" size={24} color="#FFFFFF" />
        </TouchableOpacity>
        <TouchableOpacity onPress={handleLogout}>
          <Icon name="logout" size={24} color="#FFFFFF" />
        </TouchableOpacity>
      </View>
    </View>
  );
};

export default AppBar;
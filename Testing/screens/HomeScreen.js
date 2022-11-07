/* eslint-disable prettier/prettier */
import {
  Alert,
  Image,
  StyleSheet,
  Text,
  TouchableOpacity,
  View,
  Pressable,
} from 'react-native';
import React from 'react';
import {Dimensions} from 'react-native';
import ImagePicker from 'react-native-image-crop-picker';
import ShowFeature from '../components/ShowFeature';
import {TextInput} from 'react-native-paper';
import {useState} from 'react';
import DialogInput from 'react-native-dialog-input';
import { useNavigation } from '@react-navigation/native';
export default function HomeScreen({navigation}) {
  const navi =useNavigation();
  const [isDialogVisible, setIsDialogVisible] = useState(false);
  const [isUpdateDialogVisible, setIsUpdateDialogVisible] = useState(false);
  
  const updateScreen = (id, amount, date) => {
    navi.navigate('Update', {
      invoice_id: id,
      total_amount: amount,
      date: date,
    });
  };
  const deleteData = id => {
    fetch(`http://10.0.2.2:5000/delete/${id}`, {
      method: 'DELETE',
    }).catch(error => console.log(error));
  };
  const getData= id => {
    fetch(`http://10.0.2.2:5000/get/${id}`, {
      method:'GET',
    }).then(resp => resp.json())
    .then(invoice => {
      updateScreen(invoice.invoice_id,invoice.total_amount,invoice.date);
    });
  }

  const updater = () => {
    setIsUpdateDialogVisible(true);
  };
  const deleter = () => {
    setIsDialogVisible(true);
  };

  const lister = () => {
    navigation.navigate('Show');
  };
  const adder = () => {
    navigation.navigate('Add');
  };
  return (
    <View style={styles.image}>
      <Image source={require('../assets/4Alabs.png')} />
      <TouchableOpacity style={styles.panelButton} onPress={lister}>
        <Text style={styles.text}>List of Invoices </Text>
      </TouchableOpacity>
      <TouchableOpacity style={styles.panelButton} onPress={adder}>
        <Text style={styles.text}>Add new Invoices</Text>
      </TouchableOpacity>
      <TouchableOpacity style={styles.panelButton} onPress={updater}>
        <Text style={styles.text}>Update & Look an Invoice</Text>
      </TouchableOpacity>
      <TouchableOpacity style={styles.panelButton} onPress={deleter}>
        <Text style={styles.text}>Delete Invoices</Text>
      </TouchableOpacity>
      <DialogInput
        isDialogVisible={isDialogVisible}
        title={'Deleting'}
        message={'Invoice ID to Delete'}
        submitText={'Delete'}
        closeDialog={() => {
          setIsDialogVisible(false);
        }}
        submitInput={inputText => {
          deleteData(inputText);
          setIsDialogVisible(false);
        }}
      />
      <DialogInput
        isDialogVisible={isUpdateDialogVisible}
        title={'Update & Look'}
        message={'Invoice ID to Delete or Look'}
        submitText={'Look'}
        closeDialog={() => {
          setIsUpdateDialogVisible(false);
        }}
        submitInput={inputText => {
          setIsDialogVisible(false);
          getData(inputText);
        }}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  image: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#080f4a',
  },
  panelButton: {
    width: Dimensions.get('window').width * 0.9,
    padding: 13,
    borderRadius: 10,
    backgroundColor: '#e62545',
    alignItems: 'center',
    marginVertical: 7,
    bottom: 0,
    left: Dimensions.get('window').width * 0.01,
  },
  text: {
    color: '#fff',
    fontSize: 17,
  },
});

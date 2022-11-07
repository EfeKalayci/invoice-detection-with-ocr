/* eslint-disable prettier/prettier */
import React, {useState, useEffect} from 'react';

import ShowFeature from '../components/ShowFeature';
import {
  View,
  Text,
  ActivityIndicator,
  StyleSheet,
  Button,
  FlatList,
  TouchableOpacity,
  Alert,
  ImageStore,
} from 'react-native';
import {TextInput} from 'react-native-paper';
import {Dimensions} from 'react-native';
import ImagePicker from 'react-native-image-crop-picker';
export default function AddScreen({navigation}) {
  const takePhotoFromCamera = () => {
    ImagePicker.openCamera({
      width: 300,
      height: 400,
      cropping: true,
    }).then(image => {});
  };
  const selectFromGallery = async () => {
    const image = await ImagePicker.openPicker({});
    const formData = new FormData();
    formData.append('file', { 
      uri: image.path,
      type: image.mime,
      name: image.path.split('/')[9],
    }.then(ocr(image.path.split('/')[9])));
  };

  const [invoice_id, setInvoice_id] = useState('12312');
  const [total_amount, setTotal_amount] = useState(0.0);
  const [date, setDate] = useState('');
  const [loaded, setLoaded] = useState(true);
  const ocr = async path => {
    setLoaded(false);
    fetch(`http://10.0.2.2:5000/findID/${path}`).then(resp =>
      resp
        .json()
        .then(ID => {
          setInvoice_id(ID[0].invoice_ID);
          setTotal_amount(ID[0].total);
          setDate(ID[0].date);
        })
        .then(setLoaded(true)),
    );
  };

  const insertData = () => {
    fetch('http://10.0.2.2:5000/add', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({
        invoice_id: invoice_id,
        total_amount: total_amount,
        date: date,
      }),
    })
      .then(resp => resp.json())
      .then(data => {
        navigation.navigate('Home');
      });
  };

  return (
    <>
      {loaded ? (
        <View>
          <TextInput
            style={{margin: 5}}
            label="Invoice ID"
            value={invoice_id}
            mode="outlined"
            numberOfLines={2}
            onChangeText={text => setInvoice_id(text)}
          />
          <TextInput
            style={{margin: 5}}
            label="Total Amount"
            value={total_amount}
            mode="outlined"
            numberOfLines={2}
            onChangeText={text => setTotal_amount(text)}
          />
          <TextInput
            style={{margin: 5}}
            label="Date"
            value={date}
            mode="outlined"
            numberOfLines={2}
            onChangeText={text => setDate(text)}
          />
          <TouchableOpacity
            style={styles.panelButton}
            icon="pencil"
            onPress={() => insertData()}
            title="">
            <Text style={styles.text}>Insert Invoice </Text>
          </TouchableOpacity>
          <TouchableOpacity
            style={styles.panelButton}
            onPress={takePhotoFromCamera}>
            <Text style={styles.text}>Take Photo </Text>
          </TouchableOpacity>
          <TouchableOpacity
            style={styles.panelButton}
            onPress={selectFromGallery}>
            <Text style={styles.text}>Select From Gallery</Text>
          </TouchableOpacity>
        </View>
      ) : (
        <ActivityIndicator size="large" style={styles.image} />
      )}
    </>
  );
}

const styles = StyleSheet.create({
  image: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  panelButton: {
    width: Dimensions.get('window').width * 0.9,
    padding: 13,
    borderRadius: 10,
    backgroundColor: '#e62545',
    alignItems: 'center',
    marginVertical: 7,
    bottom: 0,
    marginLeft: Dimensions.get('window').width * 0.04,
    left: Dimensions.get('window').width * 0.01,
  },
  text: {
    color: '#fff',
    fontSize: 17,
  },
});
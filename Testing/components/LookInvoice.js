/* eslint-disable prettier/prettier */
import React, {useState, useEffect} from 'react';
import {
  View,
  Text,
  TouchableOpacity,
  Dimensions,
  StyleSheet,
} from 'react-native';
import {TextInput} from 'react-native-paper';
import {useNavigation, useRoute} from '@react-navigation/native';

export default function LookInvoice({navigation}) {
  const route = useRoute();
  const data = useNavigation('data');
  const [invoice_id, setInvoice_id] = useState(`${route.params.invoice_id}`);
  console.log(data);
  const [total_amount, setTotal_amount] = useState(
    `${route.params.total_amount}`,
  );
  const [date, setDate] = useState(`${route.params.date}`);
  const deleteData = id => {
    fetch(`http://10.0.2.2:5000/delete/${id}`, {
      method: 'DELETE',
    }).catch(error => console.log(error));
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
        navigation.navigate('Show');
      });
  };
  return (
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
        onPress={() => {
          deleteData(route.params.invoice_id);
          insertData();
        }}
        title="">
        <Text style={styles.text}>Insert Invoice </Text>
      </TouchableOpacity>
      <TouchableOpacity
        style={styles.panelButton}
        icon="delete"
        onPress={() => {
          deleteData(route.params.invoice_id);
          navigation.navigate('Show');
        }}
        title="">
        <Text style={styles.text}>Delete This Invoice</Text>
      </TouchableOpacity>
    </View>
  );
}
const styles = StyleSheet.create({
  image: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  text: {
    color: '#fff',
    fontSize: 17,
  },
  butStyle: {
    position: 'absolute',
    margin: 10,
    right: 0,
    bottom: -70,
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
});

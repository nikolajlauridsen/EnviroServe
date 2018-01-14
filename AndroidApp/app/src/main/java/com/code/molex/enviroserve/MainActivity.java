package com.code.molex.enviroserve;

import android.support.v7.app.AppCompatActivity;
import android.os.Bundle;
import android.util.Log;
import android.view.View;
import android.widget.TextView;

import com.android.volley.Request;
import com.android.volley.RequestQueue;
import com.android.volley.Response;
import com.android.volley.VolleyError;
import com.android.volley.toolbox.JsonObjectRequest;
import com.android.volley.toolbox.Volley;

import org.json.JSONException;
import org.json.JSONObject;

import java.util.HashMap;

public class MainActivity extends AppCompatActivity {
    private final String errorString = "Error";

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
    }

    public HashMap<String, String> formatData(JSONObject response) throws JSONException{
        HashMap<String, String> data = new HashMap<>();
        // Extract data from JSON
        Long temperature = Math.round(response.getDouble("temp"));
        Long humidity = Math.round(response.getDouble("humid"));
        Long pressure = Math.round(response.getDouble("pressure"));
        // Format it
        data.put("temp", temperature.toString() + getString(R.string.temp_unit));
        data.put("humid", humidity.toString() + getString(R.string.humid_unit));
        data.put("pressure", pressure.toString() + getString(R.string.pressure_unit));
        return data;

    }

    public void refreshData(View view){
        // Get text placeholders
        final TextView tempText = findViewById(R.id.temp);
        final TextView humidText = findViewById(R.id.humid);
        final TextView pressureText = findViewById(R.id.pressure);

        // Prepare for sending request
        RequestQueue queue = Volley.newRequestQueue(this);
        // TODO: Don't hardcode the URL
        String url = "http://192.168.1.250:2020/climate/now";

        JsonObjectRequest dataRequest = new JsonObjectRequest
                (Request.Method.GET, url, null, new Response.Listener<JSONObject>() {
                    @Override
                    public void onResponse(JSONObject response) {
                        try{
                            // Extract values from JSON
                            Log.i("Response content", response.toString());
                            HashMap<String, String> data = formatData(response);
                            // Set text boxes
                            tempText.setText(data.get("temp"));
                            humidText.setText(data.get("humid"));
                            pressureText.setText(data.get("pressure"));
                        } catch (JSONException e) {
                            // TODO: Show a dialog box
                            tempText.setText(errorString);
                        }

                    }
                }, new Response.ErrorListener() {
                    @Override
                    public void onErrorResponse(VolleyError error) {
                        // TODO: Smart error things
                    }
                });
        // Launch.
        queue.add(dataRequest);
    }
}

package com.l1172.bleimuandroid

import android.annotation.SuppressLint
import android.content.Context
import android.location.Location
import android.location.LocationManager
import android.os.Looper
import com.google.android.gms.location.LocationAvailability
import com.google.android.gms.location.LocationCallback
import com.google.android.gms.location.LocationRequest
import com.google.android.gms.location.LocationResult
import com.google.android.gms.location.LocationServices
import com.google.android.gms.location.Priority

class LocationTracker(
    context: Context,
    private val listener: Listener,
) {
    interface Listener {
        fun onLocationUpdated(sample: LocationSample)
        fun onLocationUnavailable(message: String)
        fun onLocationStatus(message: String)
    }

    private val appContext = context.applicationContext
    private val locationManager =
        appContext.getSystemService(Context.LOCATION_SERVICE) as LocationManager
    private val fusedLocationClient = LocationServices.getFusedLocationProviderClient(appContext)

    private var tracking = false
    private var lastPublishedFixTimestampMillis: Long = Long.MIN_VALUE
    private var lastPublishedProvider: String? = null

    private val locationRequest =
        LocationRequest.Builder(Priority.PRIORITY_HIGH_ACCURACY, LOCATION_UPDATE_INTERVAL_MS)
            .setMinUpdateIntervalMillis(MIN_LOCATION_UPDATE_INTERVAL_MS)
            .setWaitForAccurateLocation(false)
            .setMaxUpdateDelayMillis(MAX_LOCATION_UPDATE_DELAY_MS)
            .build()

    private val locationCallback = object : LocationCallback() {
        override fun onLocationResult(result: LocationResult) {
            val newestLocation = result.locations.maxByOrNull(Location::getTime) ?: return
            publishLocation(newestLocation)
        }

        override fun onLocationAvailability(availability: LocationAvailability) {
            if (!availability.isLocationAvailable) {
                listener.onLocationUnavailable(
                    "GPS: waiting for a fresh fused fix. Keep location on and move outdoors if possible.",
                )
            }
        }
    }

    @SuppressLint("MissingPermission")
    fun start(): Boolean {
        val locationEnabled = isLocationEnabled()
        if (tracking) {
            return locationEnabled
        }

        lastPublishedFixTimestampMillis = Long.MIN_VALUE
        lastPublishedProvider = null

        if (!locationEnabled) {
            listener.onLocationUnavailable(
                "GPS: location services are off. CSV rows will stay blank until GPS is enabled.",
            )
            return false
        }

        fusedLocationClient.lastLocation
            .addOnSuccessListener { location ->
                location
                    ?.takeIf(::isFreshLocation)
                    ?.let(::publishLocation)
            }
            .addOnFailureListener {
                listener.onLocationStatus("GPS: unable to read cached fused location.")
            }

        fusedLocationClient.requestLocationUpdates(
            locationRequest,
            locationCallback,
            Looper.getMainLooper(),
        ).addOnFailureListener {
            listener.onLocationUnavailable(
                "GPS: fused high-accuracy updates could not start.",
            )
        }
        tracking = true
        listener.onLocationStatus("GPS: requesting fused high-accuracy updates...")
        return true
    }

    fun stop() {
        if (!tracking) {
            return
        }

        fusedLocationClient.removeLocationUpdates(locationCallback)
        tracking = false
        lastPublishedFixTimestampMillis = Long.MIN_VALUE
        lastPublishedProvider = null
    }

    private fun isLocationEnabled(): Boolean {
        return try {
            locationManager.isLocationEnabled
        } catch (_: Exception) {
            isProviderEnabled(LocationManager.GPS_PROVIDER) ||
                isProviderEnabled(LocationManager.NETWORK_PROVIDER)
        }
    }

    private fun isProviderEnabled(provider: String): Boolean {
        return try {
            locationManager.isProviderEnabled(provider)
        } catch (_: Exception) {
            false
        }
    }

    private fun publishLocation(location: Location) {
        val sample = LocationSample.fromLocation(location)
        if (sample.fixTimestampMillis != lastPublishedFixTimestampMillis ||
            sample.provider != lastPublishedProvider
        ) {
            listener.onLocationUpdated(sample)
            lastPublishedFixTimestampMillis = sample.fixTimestampMillis
            lastPublishedProvider = sample.provider
        }

        listener.onLocationStatus(
            if (isFreshLocation(location)) {
                "GPS: using fused high-accuracy fix."
            } else {
                "GPS: using cached fused fix."
            },
        )
    }

    private fun isFreshLocation(location: Location): Boolean {
        return System.currentTimeMillis() - location.time <= MAX_LOCATION_AGE_MS
    }

    companion object {
        private const val LOCATION_UPDATE_INTERVAL_MS = 2000L
        private const val MIN_LOCATION_UPDATE_INTERVAL_MS = 1000L
        private const val MAX_LOCATION_UPDATE_DELAY_MS = 2000L
        private const val MAX_LOCATION_AGE_MS = 10_000L
    }
}

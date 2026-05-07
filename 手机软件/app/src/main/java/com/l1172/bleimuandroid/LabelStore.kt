package com.l1172.bleimuandroid

import android.content.Context

object LabelStore {
    private const val PREFS_NAME = "label_prefs"
    private const val KEY_LABELS = "labels"
    private val DEFAULT_LABELS = listOf("walking", "cycling", "sitting", "standing", "scooter")

    fun getLabels(context: Context): MutableList<String> {
        val prefs = context.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE)
        val raw = prefs.getString(KEY_LABELS, null) ?: return DEFAULT_LABELS.toMutableList()
        return raw.split("\n").filter { it.isNotBlank() }.toMutableList()
    }

    fun saveLabels(context: Context, labels: List<String>) {
        context.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE)
            .edit()
            .putString(KEY_LABELS, labels.joinToString("\n"))
            .apply()
    }
}

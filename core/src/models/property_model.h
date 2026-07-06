/**
 * @file property_model.h
 * @brief Property data structures
 * @copyright Real Estate Management System
 */
#ifndef PROPERTY_MODEL_H
#define PROPERTY_MODEL_H

typedef struct {
    int id;
    char category[20];
    char listing_type[20];
    int municipal_district;
    char address[255];
    char owner_phone[20];
    int sale_price;
    int rent_deposit;
    int rent_monthly;
    int created_by;
    char created_at[30];
    char archived_at[30];
} Property;

#endif

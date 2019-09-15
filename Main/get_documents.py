
if __name__ == '__main__':
    # Mainline
    results = list_envelopes()
    print("\nEnvelopes:\n")
    pprint.pprint(results, indent=4, width=80)
    get_doc_text()

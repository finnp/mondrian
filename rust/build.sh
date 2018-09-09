cargo build --release
cp target/release/libmyrustlib.dylib myrustlib.so && python3 test.py

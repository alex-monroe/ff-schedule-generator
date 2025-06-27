# React Web Frontend for Python gRPC Server

This document outlines the tasks required to build a React-based web frontend. The goal is to provide a simple UI for sending requests to a gRPC server and displaying responses.

## Phase 1: Project Initialization and Setup
- [ ] **Task 1.1: Initialize React Application**
  - Use `create-react-app` or `npm create vite@latest my-grpc-app -- --template react-ts`.
- [ ] **Task 1.2: Install Core Dependencies**
  ```bash
  npm install @grpc/grpc-web google-protobuf
  ```
- [ ] **Task 1.3: Install Developer Dependencies**
  ```bash
  npm install -D ts-protoc-gen
  ```
  *Note:* Ensure `protoc` and `protoc-gen-grpc-web` are installed.
- [ ] **Task 1.4: Establish Project Structure**
  ```text
  /src
  ├─ /components    # React components (e.g., RequestForm, ResponseDisplay)
  ├─ /grpc          # Generated protobuf files and client code
  ├─ /services      # Service layer for gRPC calls
  ├─ App.tsx        # Main application component
  └─ main.tsx       # Application entry point
  ```

## Phase 2: gRPC-Web Code Generation
- [ ] **Task 2.1: Locate and Copy the `.proto` File**
  - Place your `.proto` definitions in a `/protos` directory.
- [ ] **Task 2.2: Generate JavaScript/TypeScript Client Code**
  ```bash
  protoc -I=./protos \
    --js_out=import_style=commonjs,binary:./src/grpc \
    --grpc-web_out=import_style=typescript,mode=grpcwebtext:./src/grpc \
    ./protos/your_service.proto
  ```
- [ ] **Task 2.3: Add Generation Script to `package.json`**
  ```json
  {
    "scripts": {
      "proto:gen": "protoc -I=./protos --js_out=import_style=commonjs,binary:./src/grpc --grpc-web_out=import_style=typescript,mode=grpcwebtext:./src/grpc ./protos/your_service.proto"
    }
  }
  ```

## Phase 3: Implement the Service Layer
- [ ] **Task 3.1: Create the gRPC Client Service**
  - Implement an `apiClient.ts` in `/src/services` that instantiates the generated client with the gRPC-web proxy URL.
- [ ] **Task 3.2: Wrap the gRPC Method Calls**
  - Provide async functions that:
    1. Accept plain objects.
    2. Build protobuf request messages.
    3. Invoke the client methods.
    4. Return a `Promise` with the response.

## Phase 4: Build React Components
- [ ] **Task 4.1: Request Form Component**
  - `/src/components/RequestForm.tsx` should render form fields for the request and a **Send Request** button.
- [ ] **Task 4.2: Response Display Component**
  - `/src/components/ResponseDisplay.tsx` displays response data or errors in a readable format and handles a loading state.
- [ ] **Task 4.3: Main App Component**
  - In `App.tsx`, manage loading, response, and error state, and pass handlers to `RequestForm`.

## Phase 5: Environment and Proxy Configuration
- [ ] **Task 5.1: Configure Environment Variables**
  - Store the gRPC-web proxy URL (e.g., `VITE_GRPC_WEB_URL`) in environment variables.
- [ ] **Task 5.2: Document the Need for a gRPC-Web Proxy**
  - Explain in `README.md` that a proxy (Envoy, NGINX, etc.) is required for browser communication.
- [ ] **Task 5.3: Provide an Example Proxy Configuration**
  ```yaml
  # ...
  - name: envoy.filters.network.http_connection_manager
    typed_config:
      "@type": type.googleapis.com/envoy.extensions.filters.network.http_connection_manager.v3.HttpConnectionManager
      stat_prefix: ingress_http
      http_filters:
        - name: envoy.filters.http.grpc_web
        - name: envoy.filters.http.cors
        - name: envoy.filters.http.router
      route_config:
        virtual_hosts:
          - name: backend
            domains: ["*"]
            routes:
              - match: { prefix: "/" }
                route:
                  cluster: your_grpc_service_cluster
                  # ...
  # ...
  ```

## Phase 6: Final Touches
- [ ] **Task 6.1: Add Basic Styling**
  - Apply CSS or a UI library (Tailwind, Material-UI, Chakra UI) to make the interface clean.
- [ ] **Task 6.2: Write a `README.md`**
  - Document how to:
    - Install dependencies (`npm install`).
    - Run the code generator (`npm run proto:gen`).
    - Start the development server (`npm run dev`).
    - Ensure a running gRPC server and configured gRPC-web proxy.
